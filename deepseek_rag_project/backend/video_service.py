import os
import cv2
import logging
import torch
import multiprocessing
import shutil
from PIL import Image
from config import Config
from qwen_vl_utils import process_vision_info

# 配置简洁的日志格式
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VideoService:
    def __init__(self):
        self.vl_model = None
        self.vl_processor = None
        self.audio_model = None
        logger.info("VideoService Initialized.")

    def _load_models_if_needed(self):
        if self.vl_model is not None:
            return

        logger.info("Loading models...")
        
        # 动态计算线程数
        total_cores = multiprocessing.cpu_count()
        compute_threads = max(1, total_cores - 4) 
        torch.set_num_threads(compute_threads)
        
        model_cache_path = Config.MODEL_CACHE_DIR

        try:
            from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
            from faster_whisper import WhisperModel
            
            # 1. 加载 Qwen2-VL (视觉)
            logger.info(f"Loading Vision Model: {Config.VISION_MODEL_ID}")
            # 🚀【核心修复】移除 quantize_dynamic
            # Qwen2-VL 对精度敏感，CPU 上 Int8 量化会导致“致盲”产生幻觉
            # 您的 128GB 内存完全足够跑 FP32
            self.vl_model = Qwen2VLForConditionalGeneration.from_pretrained(
                Config.VISION_MODEL_ID,
                torch_dtype=torch.float32, # 明确使用 FP32 保证精度
                device_map="cpu",
                cache_dir=model_cache_path,
                low_cpu_mem_usage=True
            )
            # self.vl_model.eval() # from_pretrained 默认就是 eval 模式
            
            self.vl_processor = AutoProcessor.from_pretrained(
                Config.VISION_MODEL_ID,
                cache_dir=model_cache_path
            )

            # 2. 加载 Whisper (听觉) - Whisper 的 Int8 是官方支持的，安全
            logger.info("Loading Audio Model: Faster-Whisper")
            self.audio_model = WhisperModel(
                Config.AUDIO_MODEL_SIZE, 
                device="cpu", 
                compute_type="int8", 
                cpu_threads=4,      
                download_root=os.path.join(model_cache_path, "whisper") 
            )
            
            logger.info("All models loaded successfully.")
        except Exception as e:
            logger.error(f"Model loading failed: {e}")
            raise e

    def extract_audio_text(self, video_path):
        from moviepy.editor import VideoFileClip
        if not self.audio_model: return ""
        
        logger.info("Starting audio transcription...")
        temp_audio_path = video_path + ".wav"

        try:
            video = VideoFileClip(video_path)
            if video.audio is None:
                video.close()
                return "（该视频无音轨）"
            
            video.audio.write_audiofile(temp_audio_path, codec='pcm_s16le', verbose=False, logger=None)
            video.close()
            
            segments, info = self.audio_model.transcribe(
                temp_audio_path, 
                beam_size=5, 
                language="zh", 
                vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=500),
                initial_prompt="以下是一段中文会议记录或对话，请准确转录内容。"
            )
            
            text_lines = []
            for segment in segments:
                start = int(segment.start)
                end = int(segment.end)
                text_lines.append(f"- [{start}s-{end}s]: {segment.text.strip()}")
            
            final_text = "\n".join(text_lines)
            
            if os.path.exists(temp_audio_path): 
                os.remove(temp_audio_path)
                
            return final_text if final_text else "（音频转录为空）"

        except Exception as e:
            logger.error(f"Audio extraction error: {e}")
            if os.path.exists(temp_audio_path): os.remove(temp_audio_path)
            return f"语音提取失败: {e}"

    def analyze_frames(self, video_path):
        if not self.vl_model: return ""

        logger.info("Starting visual analysis...")
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS) or 24
        
        descriptions = []
        batch_frames = []
        batch_timestamps = []
        
        frame_count = 0
        last_analysis_time = -999
        prev_frame_gray = None
        
        min_interval = 2.0 
        max_interval = Config.VIDEO_FRAME_INTERVAL
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            
            curr_time = frame_count / fps
            
            if curr_time - last_analysis_time < min_interval:
                frame_count += 1
                continue

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray_small = cv2.resize(gray, (64, 64))
            
            is_scene_change = False
            if prev_frame_gray is not None:
                diff_score = cv2.absdiff(prev_frame_gray, gray_small).mean()
                if diff_score > 30: is_scene_change = True
            else:
                is_scene_change = True

            if (curr_time - last_analysis_time >= max_interval) or is_scene_change:
                timestamp = int(curr_time)
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(frame_rgb)
                
                batch_frames.append(pil_img)
                batch_timestamps.append(timestamp)
                
                last_analysis_time = curr_time
                prev_frame_gray = gray_small
                
                if len(batch_frames) >= Config.VIDEO_BATCH_SIZE:
                    self._process_batch(batch_frames, batch_timestamps, descriptions)
                    batch_frames = []
                    batch_timestamps = []

            frame_count += 1
        
        if batch_frames:
            self._process_batch(batch_frames, batch_timestamps, descriptions)
        
        cap.release()
        return "\n".join(descriptions)

    def _process_batch(self, images, timestamps, descriptions):
        try:
            print(f"Processing batch of {len(images)} frames...", flush=True)
            
            messages_batch = []
            # 简化 Prompt，确保模型能直接回答
            system_instruction = "Describe this image in detail."
            
            for img in images:
                messages_batch.append([
                    {
                        "role": "user",
                        "content": [
                            {"type": "image", "image": img, "max_pixels": Config.VIDEO_MAX_PIXELS},
                            {"type": "text", "text": system_instruction}
                        ]
                    }
                ])
            
            texts = [
                self.vl_processor.apply_chat_template(msg, tokenize=False, add_generation_prompt=True)
                for msg in messages_batch
            ]
            
            image_inputs, video_inputs = process_vision_info(messages_batch)
            
            inputs = self.vl_processor(
                text=texts,
                images=image_inputs,
                videos=video_inputs,
                padding=True,
                return_tensors="pt"
            )
            # 确保输入数据也在 CPU
            inputs = inputs.to("cpu")
            
            # 推理
            generated_ids = self.vl_model.generate(**inputs, max_new_tokens=128)
            
            generated_ids_trimmed = [
                out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
            ]
            output_texts = self.vl_processor.batch_decode(
                generated_ids_trimmed, skip_special_tokens=True
            )
            
            for i, text in enumerate(output_texts):
                clean_text = text.replace("\n", " ").strip()
                # 如果输出为空，记录警告
                if not clean_text:
                    logger.warning(f"Frame at {timestamps[i]}s produced empty description.")
                    clean_text = "(无法识别画面内容)"
                descriptions.append(f"[{timestamps[i]}s]: {clean_text}")
                
        except Exception as e:
            logger.error(f"Batch inference failed: {e}")

    def process_video(self, video_path):
        self._load_models_if_needed()
        logger.info(f"Processing video: {os.path.basename(video_path)}")
        
        visual_desc = self.analyze_frames(video_path)
        audio_text = self.extract_audio_text(video_path)
        
        final_report = f"""
# 视频智能分析报告
文件名: {os.path.basename(video_path)}

## 1. 视觉摘要 (Visual)
{visual_desc}

## 2. 语音转录 (Audio)
{audio_text}
"""
        return final_report

_video_service = None
def get_video_service():
    global _video_service
    if _video_service is None:
        _video_service = VideoService()
    return _video_service
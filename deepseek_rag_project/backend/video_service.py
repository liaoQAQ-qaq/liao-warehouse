import os
import cv2
import logging
import torch
import multiprocessing
# 🚀【修复】补回缺失的 Image 引用
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
from config import Config
from qwen_vl_utils import process_vision_info

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
        
        # 线程优化
        total_cores = multiprocessing.cpu_count()
        compute_threads = max(1, total_cores - 6) 
        torch.set_num_threads(compute_threads)
        
        model_cache_path = Config.MODEL_CACHE_DIR

        try:
            # 强制使用 Qwen2.5 专用类
            from transformers import Qwen2_5_VLForConditionalGeneration, AutoProcessor
            from faster_whisper import WhisperModel
            
            logger.info(f"Loading Vision Model from: {Config.VISION_MODEL_ID}")
            logger.info("🚀 正在强制使用 Qwen2_5_VLForConditionalGeneration 加载...")

            self.vl_model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
                Config.VISION_MODEL_ID,
                torch_dtype=torch.float32, 
                device_map="cpu",
                low_cpu_mem_usage=True
            )
            
            self.vl_processor = AutoProcessor.from_pretrained(
                Config.VISION_MODEL_ID
            )

            logger.info("Loading Audio Model: Faster-Whisper")
            self.audio_model = WhisperModel(
                Config.AUDIO_MODEL_SIZE, 
                device="cpu", 
                compute_type="int8", 
                cpu_threads=4,      
                download_root=os.path.join(model_cache_path, "whisper") 
            )
            
            logger.info("✅ All models loaded successfully.")
        except ImportError as e:
            logger.error(f"❌ 致命错误: 无法导入 Qwen2.5 专用类。请更新 transformers。")
            raise e
        except Exception as e:
            logger.error(f"❌ Model loading failed: {e}")
            raise e

    def extract_audio_text(self, video_path):
        from moviepy.editor import VideoFileClip
        if not self.audio_model: return ""
        
        logger.info("🎤 [Audio] 正在提取音频...")
        temp_audio_path = video_path + ".wav"

        try:
            video = VideoFileClip(video_path)
            if video.audio is None:
                video.close()
                return "（该视频无音轨）"
            
            video.audio.write_audiofile(temp_audio_path, codec='pcm_s16le', verbose=False, logger=None)
            video.close()
            
            # Whisper 转录
            segments, info = self.audio_model.transcribe(
                temp_audio_path, 
                beam_size=5, 
                language="zh", 
                # 注意：如果视频主要是环境音（如狗叫、风声），VAD 可能会过滤掉所有内容
                # 如果发现音频一直是空的，可以将 vad_filter 改为 False
                vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=500),
                initial_prompt="以下是一段中文会议记录或对话，请准确转录内容。"
            )
            
            text_lines = []
            print(f"\n--- 🎤 音频识别流 ---")
            for segment in segments:
                text = segment.text.strip()
                print(f"🎤 {text}") 
                text_lines.append(f"[{int(segment.start)}s]: {text}")
            print(f"---------------------\n")
            
            if os.path.exists(temp_audio_path): os.remove(temp_audio_path)
            
            # 如果 VAD 过滤了所有内容（比如只有狗叫声），给一个提示
            if not text_lines:
                logger.info("ℹ️ [Audio] 未检测到有效语音（可能是纯背景音）")
                return "（未检测到清晰语音，可能是环境音）"
                
            return "\n".join(text_lines)

        except Exception as e:
            logger.error(f"Audio error: {e}")
            if os.path.exists(temp_audio_path): os.remove(temp_audio_path)
            return f"语音提取失败: {e}"

    def analyze_frames(self, video_path):
        if not self.vl_model: return ""

        logger.info("👁️ [Vision] 开始视觉分析...")
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS) or 24
        
        descriptions = []
        batch_frames = []
        batch_timestamps = []
        
        frame_count = 0
        last_analysis_time = -999
        min_interval = 2.0 
        max_interval = Config.VIDEO_FRAME_INTERVAL
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            
            curr_time = frame_count / fps
            
            if curr_time - last_analysis_time >= max_interval:
                timestamp = int(curr_time)
                # 转换颜色空间
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # 🚀 这里需要使用 Image 类
                pil_img = Image.fromarray(frame_rgb)
                
                batch_frames.append(pil_img)
                batch_timestamps.append(timestamp)
                last_analysis_time = curr_time
                
                if len(batch_frames) >= Config.VIDEO_BATCH_SIZE:
                    self._process_batch(batch_frames, batch_timestamps, descriptions)
                    batch_frames = []
                    batch_timestamps = []

            frame_count += 1
        
        if batch_frames:
            self._process_batch(batch_frames, batch_timestamps, descriptions)
        
        cap.release()
        logger.info("✅ [Vision] 视觉分析结束")
        return "\n".join(descriptions)

    def _process_batch(self, images, timestamps, descriptions):
        try:
            print(f"⚡ [Vision] 分析 {len(images)} 帧...", flush=True)
            
            messages_batch = []
            prompt = "Describe this image in detail."
            
            for img in images:
                messages_batch.append([
                    {
                        "role": "user",
                        "content": [
                            {"type": "image", "image": img, "max_pixels": Config.VIDEO_MAX_PIXELS},
                            {"type": "text", "text": prompt}
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
            inputs = inputs.to("cpu")
            
            generated_ids = self.vl_model.generate(**inputs, max_new_tokens=128)
            
            generated_ids_trimmed = [
                out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
            ]
            output_texts = self.vl_processor.batch_decode(
                generated_ids_trimmed, skip_special_tokens=True
            )
            
            for i, text in enumerate(output_texts):
                clean_text = text.replace("\n", " ").strip()
                descriptions.append(f"[{timestamps[i]}s]: {clean_text}")
                
        except Exception as e:
            logger.error(f"Batch inference error: {e}")

    def process_video(self, video_path):
        self._load_models_if_needed()
        logger.info(f"🎬 开始并行处理: {os.path.basename(video_path)}")
        
        with ThreadPoolExecutor(max_workers=2) as executor:
            future_vision = executor.submit(self.analyze_frames, video_path)
            future_audio = executor.submit(self.extract_audio_text, video_path)
            
            visual_desc = future_vision.result()
            audio_text = future_audio.result()
        
        final_report = f"""
# 视频智能分析报告
文件名: {os.path.basename(video_path)}

## 1. 视觉摘要
{visual_desc}

## 2. 语音转录
{audio_text}
"""
        return final_report

_video_service = None
def get_video_service():
    global _video_service
    if _video_service is None:
        _video_service = VideoService()
    return _video_service
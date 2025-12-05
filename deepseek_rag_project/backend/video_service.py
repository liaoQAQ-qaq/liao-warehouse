import os
import cv2
import logging
import torch
import shutil
import numpy as np
import threading
import multiprocessing
from PIL import Image
from config import Config
from concurrent.futures import ThreadPoolExecutor
from qwen_vl_utils import process_vision_info # 确保已安装 qwen-vl-utils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoService:
    _instance_lock = threading.Lock()
    
    def __init__(self):
        self.vl_model = None
        self.vl_processor = None
        self.audio_model = None
        logger.info("⏳ VideoService (批处理+量化优化版) 已实例化...")

    def _load_models_if_needed(self):
        if self.vl_model is not None:
            return

        with self._instance_lock:
            if self.vl_model is not None: return

            print("\n" + "="*50)
            print("🚀 [VideoService] 正在加载模型...")
            
            # 🚀 优化1: 动态线程
            total_cores = multiprocessing.cpu_count()
            compute_threads = max(1, total_cores - 4) 
            torch.set_num_threads(compute_threads)
            print(f"🔥 检测到 {total_cores} 核 CPU，已分配 {compute_threads} 个计算线程")
            
            model_cache_path = Config.MODEL_CACHE_DIR

            try:
                from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
                from faster_whisper import WhisperModel
                
                # 1. 加载 Qwen2-VL
                print(f"   1/2 正在加载视觉模型 ({Config.VISION_MODEL_ID})...")
                model = Qwen2VLForConditionalGeneration.from_pretrained(
                    Config.VISION_MODEL_ID,
                    dtype=torch.float32, 
                    device_map="cpu",
                    cache_dir=model_cache_path,
                    low_cpu_mem_usage=True
                )
                
                # 🚀 优化2: 动态量化 (Int8)
                print("   ⚡ 正在应用 CPU 动态量化 (Int8)...")
                self.vl_model = torch.quantization.quantize_dynamic(
                    model, {torch.nn.Linear}, dtype=torch.qint8
                )
                self.vl_model.eval()
                
                self.vl_processor = AutoProcessor.from_pretrained(
                    Config.VISION_MODEL_ID,
                    cache_dir=model_cache_path
                )

                # 2. 加载 Whisper
                print(f"   2/2 正在加载语音模型 (Faster-Whisper)...")
                self.audio_model = WhisperModel(
                    Config.AUDIO_MODEL_SIZE, 
                    device="cpu", 
                    compute_type="int8", 
                    cpu_threads=4,      
                    download_root=os.path.join(model_cache_path, "whisper") 
                )
                
                print("✅ 模型加载与优化完毕！")
            except Exception as e:
                logger.error(f"❌ 模型加载失败: {e}")
                import traceback
                traceback.print_exc()
                raise e
            print("="*50 + "\n")

    def extract_audio_text(self, video_path):
        from moviepy.editor import VideoFileClip
        if not self.audio_model: return ""
        
        logger.info("🎤 [Whisper] 正在提取语音...")
        try:
            audio_path = video_path + ".mp3"
            video = VideoFileClip(video_path)
            if video.audio is None:
                video.close()
                return "（该视频无音轨）"
            
            video.audio.write_audiofile(audio_path, verbose=False, logger=None)
            video.close()
            
            segments, info = self.audio_model.transcribe(
                audio_path, 
                beam_size=5, 
                language="zh", 
                vad_filter=True 
            )
            
            text_content = ""
            for segment in segments:
                start = int(segment.start)
                end = int(segment.end)
                text_content += f"[{start}s->{end}s] {segment.text}\n"
            
            if os.path.exists(audio_path): os.remove(audio_path)
            return text_content
        except Exception as e:
            logger.error(f"语音提取出错: {e}")
            return f"语音提取失败: {e}"

    def analyze_frames(self, video_path):
        """🚀 核心重构：支持 Batch 处理与高清分析"""
        if not self.vl_model: return ""

        logger.info(f"👁️ [Qwen2-VL] 开始智能批处理视觉分析...")
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS) or 24
        
        descriptions = []
        
        # 批处理 Buffer
        batch_frames = []      # 存 PIL Image
        batch_timestamps = []  # 存 时间戳
        
        frame_count = 0
        last_analysis_time = -999
        prev_frame_gray = None
        
        min_interval = 2.0 
        max_interval = Config.VIDEO_FRAME_INTERVAL
        
        # 🚀 优化3: 批处理循环
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            
            curr_time = frame_count / fps
            
            # 1. 快速跳过逻辑
            if curr_time - last_analysis_time < min_interval:
                frame_count += 1
                continue

            # 2. 场景变化检测 (灰度小图)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray_small = cv2.resize(gray, (64, 64))
            
            is_scene_change = False
            if prev_frame_gray is not None:
                diff_score = cv2.absdiff(prev_frame_gray, gray_small).mean()
                if diff_score > 30: is_scene_change = True
            else:
                is_scene_change = True

            # 3. 决定是否入队
            if (curr_time - last_analysis_time >= max_interval) or is_scene_change:
                timestamp = int(curr_time)
                
                # 🚀 优化4: 画质提升，不再强制 resize 到 448
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(frame_rgb)
                
                batch_frames.append(pil_img)
                batch_timestamps.append(timestamp)
                
                last_analysis_time = curr_time
                prev_frame_gray = gray_small
                
                # 4. 批处理触发：当积攒到 BATCH_SIZE (8帧) 时，一次性发送给 CPU
                if len(batch_frames) >= Config.VIDEO_BATCH_SIZE:
                    self._process_batch(batch_frames, batch_timestamps, descriptions)
                    batch_frames = []
                    batch_timestamps = []

            frame_count += 1
        
        # 处理剩余的尾帧
        if batch_frames:
            self._process_batch(batch_frames, batch_timestamps, descriptions)
        
        cap.release()
        return "\n".join(descriptions)

    def _process_batch(self, images, timestamps, descriptions):
        """内部方法：执行 Batch 推理"""
        try:
            print(f"⚡ [Batch] 正在并行处理 {len(images)} 帧...")
            
            # 构造 Batch Prompt
            messages_batch = []
            system_instruction = "你是一个严谨的视频分析员。请客观描述画面，不要猜测，不要编造内容。如果文字模糊，就说无法识别。"
            for img in images:
                messages_batch.append([
                    {
                        "role": "user",
                        "content": [
                            # Qwen2-VL 会自动处理 resize，我们只需控制 max_pixels
                            {"type": "image", "image": img, "max_pixels": Config.VIDEO_MAX_PIXELS},
                            {"type": "text", "text": f"{system_instruction}\n简要描述画面中的关键文字标题、人物动作或环境变化。"}
                        ]
                    }
                ])
            
            # 预处理
            texts = [
                self.vl_processor.apply_chat_template(msg, tokenize=False, add_generation_prompt=True)
                for msg in messages_batch
            ]
            
            image_inputs, video_inputs = process_vision_info(messages_batch)
            
            # 这里的 batching 发生在 inputs 构建阶段
            inputs = self.vl_processor(
                text=texts,
                images=image_inputs,
                videos=video_inputs,
                padding=True,
                return_tensors="pt"
            )
            inputs = inputs.to("cpu") # 确保在 CPU
            
            # 推理
            # Batch generate: 输入张量已经是 [Batch, ...] 维度
            generated_ids = self.vl_model.generate(**inputs, max_new_tokens=128)
            
            # 解码
            generated_ids_trimmed = [
                out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
            ]
            output_texts = self.vl_processor.batch_decode(
                generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
            )
            
            # 结果回填
            for i, text in enumerate(output_texts):
                desc_line = f"[{timestamps[i]}秒]: {text}"
                print(desc_line)
                descriptions.append(desc_line)
                
        except Exception as e:
            logger.error(f"❌ Batch 推理失败: {e}")

    def process_video(self, video_path):
        self._load_models_if_needed()
        logger.info(f"🎬 开始处理: {os.path.basename(video_path)}")
        
        # 视觉分析 (现在是 Batch 的)
        # 注意：由于 analyze_frames 内部已经是用尽了 CPU 核心，这里再用 ThreadPoolExecutor 
        # 和 audio 并行可能会导致资源争抢。
        # 鉴于 audio 比较快，我们改成串行，或者让 audio 在后台跑。
        # 为了稳定性，这里改为简单的串行（先视觉后听觉，或者反之），
        # 因为视觉现在能吃满 32 核，不宜分心。
        
        visual_desc = self.analyze_frames(video_path)
        audio_text = self.extract_audio_text(video_path)
        
        final_report = f"""
# 视频多模态分析报告
文件名: {os.path.basename(video_path)}
分析策略: 动态量化(Int8) + 32核批处理 + 高清采样

## 1. 视觉画面记录
{visual_desc}

## 2. 语音转录内容
{audio_text}
"""
        logger.info("✅ 视频报告生成完成")
        return final_report

_video_service = None
def get_video_service():
    global _video_service
    if _video_service is None:
        _video_service = VideoService()
    return _video_service
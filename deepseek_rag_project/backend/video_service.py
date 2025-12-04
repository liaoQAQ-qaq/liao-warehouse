import os
import cv2
import logging
import torch
import shutil
import numpy as np
from PIL import Image
from config import Config
from concurrent.futures import ThreadPoolExecutor
import threading

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoService:
    _instance_lock = threading.Lock()
    
    def __init__(self):
        self.vl_model = None
        self.vl_processor = None
        self.audio_model = None
        logger.info("⏳ VideoService (CPU 极速优化版) 已实例化...")

    def _load_models_if_needed(self):
        if self.vl_model is not None:
            return

        with self._instance_lock:
            if self.vl_model is not None: return

            print("\n" + "="*50)
            print("🚀 [VideoService] 正在加载模型...")
            print("🔥 检测到多核 CPU，正在应用推理加速策略...")
            
            # 🚀 策略1: 限制 Torch 线程数，避免过多线程导致上下文切换开销
            torch.set_num_threads(16) 
            
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            model_cache_path = os.path.join(project_root, "model_cache")

            try:
                from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
                from faster_whisper import WhisperModel
                
                # 1. 加载 Qwen2-VL (视觉)
                print(f"   1/2 正在加载视觉模型 ({Config.VISION_MODEL_ID})...")
                self.vl_model = Qwen2VLForConditionalGeneration.from_pretrained(
                    Config.VISION_MODEL_ID,
                    dtype=torch.float32, # ✅ 修复：使用 correct 参数名 dtype
                    device_map="cpu",
                    cache_dir=model_cache_path,
                    low_cpu_mem_usage=True
                ).eval()
                
                self.vl_processor = AutoProcessor.from_pretrained(
                    Config.VISION_MODEL_ID,
                    cache_dir=model_cache_path
                )

                # 2. 加载 Whisper (听觉)
                print(f"   2/2 正在加载语音模型 (Faster-Whisper)...")
                self.audio_model = WhisperModel(
                    Config.AUDIO_MODEL_SIZE, 
                    device="cpu", 
                    compute_type="int8", # CPU 上 Int8 量化是必须的
                    cpu_threads=16,      
                    download_root=os.path.join(model_cache_path, "whisper") 
                )
                
                print("✅ 模型加载完毕！")
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
        """使用 Qwen2-VL 进行智能抽帧与分析"""
        from qwen_vl_utils import process_vision_info
        
        if not self.vl_model: return ""

        logger.info(f"👁️ [Qwen2-VL] 开始智能视觉分析...")
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS) or 24
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        descriptions = []
        frame_count = 0
        last_analysis_time = -999
        prev_frame_gray = None
        
        # 🚀 策略2: 智能跳帧逻辑
        # 只有当画面变化显著 或 距离上次分析超过一定时间(比如8秒) 才进行分析
        # 最小分析间隔设置为 2 秒，防止太频繁
        min_interval = 2.0 
        max_interval = Config.VIDEO_FRAME_INTERVAL # 默认 8秒
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            
            curr_time = frame_count / fps
            
            # 1. 快速跳过：如果距离上次分析还不到最小间隔，直接跳过，连 resize 都不做
            if curr_time - last_analysis_time < min_interval:
                frame_count += 1
                continue

            # 2. 场景变化检测
            # 将画面缩小到 64x64 进行快速灰度对比
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray_small = cv2.resize(gray, (64, 64))
            
            is_scene_change = False
            if prev_frame_gray is not None:
                # 计算两帧的差异程度
                diff_score = cv2.absdiff(prev_frame_gray, gray_small).mean()
                # 阈值 30：表示画面有明显变化（动作、切换PPT等）
                if diff_score > 30: 
                    is_scene_change = True
            else:
                is_scene_change = True # 第一帧必做

            # 3. 决定是否分析
            # 条件：(超过最大等待时间) OR (画面发生了剧烈变化)
            if (curr_time - last_analysis_time >= max_interval) or is_scene_change:
                
                timestamp = int(curr_time)
                # 🚀 策略3: 暴力压缩图片尺寸
                # 限制最大边长为 448，大幅减少 Token 数量，CPU 推理提速 3-5 倍
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, _ = frame_rgb.shape
                target_size = 448
                scale = target_size / max(h, w)
                if scale < 1:
                    new_w, new_h = int(w * scale), int(h * scale)
                    frame_rgb = cv2.resize(frame_rgb, (new_w, new_h))
                
                pil_img = Image.fromarray(frame_rgb)
                
                messages = [{
                    "role": "user",
                    "content": [
                        {"type": "image", "image": pil_img},
                        {"type": "text", "text": "简要描述画面中的关键文字标题、人物动作或环境变化。"}
                    ]
                }]
                
                try:
                    text = self.vl_processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
                    image_inputs, video_inputs = process_vision_info(messages)
                    inputs = self.vl_processor(
                        text=[text],
                        images=image_inputs,
                        videos=video_inputs,
                        padding=True,
                        return_tensors="pt"
                    )
                    inputs = inputs.to("cpu")
                    
                    # 🚀 策略4: 减少生成长度 (max_new_tokens 128 足够描述画面)
                    generated_ids = self.vl_model.generate(**inputs, max_new_tokens=128)
                    generated_ids_trimmed = [
                        out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
                    ]
                    output_text = self.vl_processor.batch_decode(
                        generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
                    )[0]
                    
                    desc_line = f"[{timestamp}秒]: {output_text}"
                    print(desc_line)
                    descriptions.append(desc_line)
                    
                    # 更新状态
                    last_analysis_time = curr_time
                    prev_frame_gray = gray_small
                    
                except Exception as e:
                    logger.warning(f"帧分析出错: {e}")

            frame_count += 1
        
        cap.release()
        return "\n".join(descriptions)

    def process_video(self, video_path):
        self._load_models_if_needed()
        logger.info(f"🎬 开始并行处理: {os.path.basename(video_path)}")
        
        # 使用线程池并行处理视觉和听觉
        with ThreadPoolExecutor(max_workers=2) as executor:
            future_vision = executor.submit(self.analyze_frames, video_path)
            future_audio = executor.submit(self.extract_audio_text, video_path)
            
            visual_desc = future_vision.result()
            audio_text = future_audio.result()
        
        final_report = f"""
# 视频多模态分析报告
文件名: {os.path.basename(video_path)}
分析策略: 智能关键帧检测 + 语音转录

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
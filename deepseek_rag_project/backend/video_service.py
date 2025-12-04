import os
import cv2
import logging
import torch
import shutil
from PIL import Image
from config import Config

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoService:
    def __init__(self):
        self.vl_model = None
        self.vl_processor = None
        self.audio_model = None
        logger.info("⏳ VideoService (Pro版) 已实例化...")

    def _load_models_if_needed(self):
        if self.vl_model is not None:
            return

        print("\n" + "="*50)
        print("🚀 [VideoService] 正在加载高性能模型 (32核 CPU 加速中)...")
        print("   这可能需要 2-3 分钟，请耐心等待...")
        
        # 获取绝对路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        model_cache_path = os.path.join(project_root, "model_cache")

        try:
            from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
            from faster_whisper import WhisperModel
            
            # 1. 加载 Qwen2-VL-7B (视觉)
            print(f"   1/2 正在加载视觉模型 ({Config.VISION_MODEL_ID})...")
            self.vl_model = Qwen2VLForConditionalGeneration.from_pretrained(
                Config.VISION_MODEL_ID,
                torch_dtype=torch.float32, # CPU 必须用 float32
                device_map="cpu",
                cache_dir=model_cache_path,
                low_cpu_mem_usage=True
            ).eval()
            
            self.vl_processor = AutoProcessor.from_pretrained(
                Config.VISION_MODEL_ID,
                cache_dir=model_cache_path
            )

            # 2. 加载 Whisper Large-v3 (听觉)
            print(f"   2/2 正在加载语音模型 (Faster-Whisper {Config.AUDIO_MODEL_SIZE})...")
            # 构造 whisper 模型的本地路径
            # 注意：faster-whisper 下载的文件夹名通常是 "models--Systran--faster-whisper-large-v3" 下的 snapshots/xxx
            # 这里我们让它自动去 cache 目录找，如果找不到会自动下载（但我们前面已经下载过了）
            self.audio_model = WhisperModel(
                Config.AUDIO_MODEL_SIZE, 
                device="cpu", 
                compute_type="int8", # int8 量化，在 CPU 上速度快且精度几乎不降
                download_root=os.path.join(model_cache_path, "whisper") 
            )
            
            print("✅ 顶配模型加载完毕！")
        except Exception as e:
            logger.error(f"❌ 模型加载失败: {e}")
            # 打印详细错误栈
            import traceback
            traceback.print_exc()
            raise e
        print("="*50 + "\n")

    def extract_audio_text(self, video_path):
        from moviepy.editor import VideoFileClip
        if not self.audio_model: return ""
        
        logger.info("🎤 [Whisper] 正在进行高精度语音转录...")
        try:
            audio_path = video_path + ".mp3"
            video = VideoFileClip(video_path)
            if video.audio is None:
                video.close()
                return "（该视频无音轨）"
            
            video.audio.write_audiofile(audio_path, verbose=False, logger=None)
            video.close()
            
            # beam_size=5 提升准确率
            segments, info = self.audio_model.transcribe(
                audio_path, 
                beam_size=5, 
                language="zh", # 强制中文，或去掉自动检测
                vad_filter=True # 自动过滤静音片段
            )
            
            text_content = ""
            for segment in segments:
                # 格式化时间戳 [00:10 -> 00:15] 文本
                start = int(segment.start)
                end = int(segment.end)
                text_content += f"[{start}s->{end}s] {segment.text}\n"
            
            if os.path.exists(audio_path): os.remove(audio_path)
            return text_content
        except Exception as e:
            logger.error(f"语音提取出错: {e}")
            return f"语音提取失败: {e}"

    def analyze_frames(self, video_path):
        """使用 Qwen2-VL 进行深度画面理解 (自带OCR)"""
        from qwen_vl_utils import process_vision_info
        
        if not self.vl_model: return ""

        logger.info(f"👁️ [Qwen2-VL] 开始逐帧深度分析 (间隔 {Config.VIDEO_FRAME_INTERVAL}秒)...")
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS) or 24
        interval = int(fps * Config.VIDEO_FRAME_INTERVAL)
        
        descriptions = []
        frame_count = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            
            if frame_count % interval == 0:
                timestamp = int(frame_count // fps)
                pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                
                # Qwen2-VL 提示词：要求其做 OCR 并描述细节
                # 32核 CPU 可以扛得住稍微长一点的生成
                messages = [{
                    "role": "user",
                    "content": [
                        {"type": "image", "image": pil_img},
                        {"type": "text", "text": "请详细描述这张画面的内容。1. 如果是软件界面或文档，请准确提取上面的文字标题和关键内容。2. 如果是现实场景，请描述人物动作和环境细节。"}
                    ]
                }]
                
                try:
                    # 预处理
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
                    
                    # 推理 (max_new_tokens 可以适当调大，因为 7B 模型废话少，比较精准)
                    generated_ids = self.vl_model.generate(**inputs, max_new_tokens=256)
                    generated_ids_trimmed = [
                        out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
                    ]
                    output_text = self.vl_processor.batch_decode(
                        generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
                    )[0]
                    
                    # 实时打印进度
                    desc_line = f"[{timestamp}秒画面]: {output_text}"
                    print(desc_line)
                    descriptions.append(desc_line)
                    
                except Exception as e:
                    logger.warning(f"帧分析出错: {e}")

            frame_count += 1
        
        cap.release()
        return "\n".join(descriptions)

    def process_video(self, video_path):
        self._load_models_if_needed()
        logger.info(f"🎬 开始处理: {os.path.basename(video_path)}")
        
        # 1. 视觉分析 (Qwen2-VL-7B)
        visual_desc = self.analyze_frames(video_path)
        
        # 2. 听觉分析 (Whisper-Large-v3)
        audio_text = self.extract_audio_text(video_path)
        
        # 3. 汇总报告
        final_report = f"""
# 视频多模态深度分析报告
文件名: {os.path.basename(video_path)}
分析模型: Qwen2-VL-7B (视觉) + Whisper-Large-v3 (语音)

## 1. 视觉与OCR分析记录
{visual_desc}

## 2. 语音转录记录
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
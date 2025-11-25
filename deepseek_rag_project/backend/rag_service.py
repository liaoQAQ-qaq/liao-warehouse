from llama_index.core import PromptTemplate
from vector_store import get_vector_service

class RAGService:
    def __init__(self):
        self.vector_service = get_vector_service()
        self.query_engine = self.vector_service.get_query_engine()
        
        # 提示词模板 (保持不变)
        qa_prompt_tmpl_str = (
            "你是一个智能且严谨的企业知识库助手。\n"
            "你的任务是基于下方的[知识库]片段，回答用户的提问。\n"
            "\n"
            "---------------------\n"
            "[知识库]:\n"
            "{context_str}\n"
            "---------------------\n"
            "\n"
            "用户问题: {query_str}\n"
            "\n"
            "[回答逻辑]:\n"
            "1. **关于你的身份**：如果用户问“你是谁”、“介绍一下你自己”，请回答：“我是您的企业知识库AI助手，可以帮您分析简历、查询技术文档或解答公司政策。”\n"
            "2. **关于用户的身份**：如果用户问“我是谁”、“我的名字是什么”、“介绍一下我”，请**立刻从[参考文档]中寻找**某人的简历、个人介绍或基本信息。\n"
            "   - 如果找到了（例如看到了'姓名：廖振豪'），请回答：“根据文档，您应该是 **廖振豪**。您的基本情况如下……”并简要总结文档内容。\n"
            "   - 如果文档里完全没有个人信息，请回答：“知识库中暂时没有找到关于您的个人信息文件。”\n"
            "3. **其他问题**：直接根据知识库回答。如果文档里没有答案，请直接说“知识库中未找到相关信息”。\n"
            "\n"
            "回答: "
        )
        
        self.qa_prompt = PromptTemplate(qa_prompt_tmpl_str)
        
        self.query_engine.update_prompts(
            {"response_synthesizer:text_qa_template": self.qa_prompt}
        )

    async def chat_stream(self, question: str):
        """流式对话生成 (纯净版 - 异步非阻塞)"""
        
        # 使用 aquery (异步查询)
        streaming_response = await self.query_engine.aquery(question)
        async for text in streaming_response.async_response_gen():
            yield text

# 单例
_rag = None
def get_rag_service():
    global _rag
    if _rag is None:
        _rag = RAGService()
    return _rag
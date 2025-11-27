import json
import re
from config import Config
from vector_store import get_vector_service
from prompts import get_qa_prompt_template
from llama_index.core import Settings
from llama_index.core.llms import ChatMessage, MessageRole

class RAGService:
    def __init__(self):
        self.vector_service = get_vector_service()
        self.retriever = self.vector_service.index.as_retriever(similarity_top_k=5)
        self.qa_prompt = get_qa_prompt_template()

    def format_docs_with_id(self, nodes):
        formatted_str = ""
        file_groups = {}
        
        for node in nodes:
            file_name = node.node.metadata.get("file_name", "未知文件")
            score = node.score if node.score else 0.0
            content = node.node.get_content().replace('\n', ' ')
            
            if file_name not in file_groups:
                file_groups[file_name] = {"content": [], "max_score": 0.0}
            
            file_groups[file_name]["content"].append(content)
            if score > file_groups[file_name]["max_score"]:
                file_groups[file_name]["max_score"] = score

        sorted_files = sorted(file_groups.items(), key=lambda x: x[1]['max_score'], reverse=True)
        
        for idx, (file_name, data) in enumerate(sorted_files):
            combined_content = "... ".join(data["content"])
            formatted_str += f"[{idx+1}] (来源: {file_name}): {combined_content}\n\n"
            
        return formatted_str, sorted_files

    async def chat_stream(self, question: str):
        # 1. 检索
        nodes_with_score = await self.retriever.aretrieve(question)
        
        if not nodes_with_score:
            yield "知识库中未找到相关信息。"
            return

        # 2. 格式化
        context_str, sorted_files = self.format_docs_with_id(nodes_with_score)
        
        # 3. 组装 Prompt
        fmt_prompt = self.qa_prompt.format(context_str=context_str, query_str=question)
        
        # 4. 调用 LLM
        messages = [ChatMessage(role=MessageRole.USER, content=fmt_prompt)]
        full_answer = ""
        
        response_gen = await Settings.llm.astream_chat(messages)
        
        async for response in response_gen:
            content = response.delta
            full_answer += content
            yield content

        # 5. 引用过滤逻辑 (增加图片豁免)
        cited_indices = set()
        matches = re.findall(r'\[(\d+)\]', full_answer)
        for m in matches:
            cited_indices.add(int(m))

        source_data = []
        for idx, (file_name, data) in enumerate(sorted_files):
            current_id = idx + 1
            
            # 🚀【核心优化】图片特权逻辑
            # 如果是图片且排第一，即使没被引用也显示（防止看图说话丢失来源）
            is_image = file_name.lower().endswith(('.jpg', '.png', '.jpeg'))
            is_top_result = (idx == 0)
            
            if current_id in cited_indices:
                source_data.append({
                    "id": current_id,
                    "name": file_name,
                    "score": round(data["max_score"], 2)
                })
            elif is_image and is_top_result:
                source_data.append({
                    "id": current_id,
                    "name": file_name,
                    "score": round(data["max_score"], 2)
                })

        # 6. 发送 JSON
        if source_data:
            yield f"__SOURCES__{json.dumps(source_data)}"

_rag = None
def get_rag_service():
    global _rag
    if _rag is None:
        _rag = RAGService()
    return _rag
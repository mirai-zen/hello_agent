import os
from serpapi import SerpApiClient

def search(query: str)-> str:
    print(f"🔍 正在执行 [SerpAPI] 网页搜索: {query}")
    
    try:
        api_key = os.getenv("SERPAPI_API_KEY")
        if not api_key:
            return "错误：SERPAPI_API_KEY 未在 .env 文件中配置"
        
        params = {
            "engine": "google",
            "q": query,
            "api_key": api_key,
            "gl": "cn", 
            "hl": "zh-cn",
        }
        
        client = SerpApiClient(params)
        result = client.get_dict()
        
        # 智能解析: 优先寻找最直接的答案
        if "answer_box_list" in result:
            return "\n".join(result["answer_box_list"])
        if "answer_box" in result and "answer" in result['answer_box']:
            return result['answer_box']['answer']
        if "knowledge_graph" in result and "description" in result['knowledge_graph']:
            return result['knowledge_graph']['description']
        if "organic_results" in result and result['organic_results']:
            snippets = [
                f"[{i+1}] {res.get('title','')}\n{res.get('snippet','')}"
                for i, res in enumerate(result['organic_results'][:3])
            ]
            return "\n\n".join(snippets)
        
        return f"对不起，没有找到关于 '{query}' 的信息。"
    except Exception as e:
        return f"搜索时发生错误： {e}"
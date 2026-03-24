import os
from typing import Any, Dict, Optional
from hello_agents.tools import Tool

class SearchTool(Tool):
    """
    智能混合搜索工具

    支持多种搜索引擎后端，智能选择最佳搜索源:
    1. 混合模式 (hybrid) - 智能选择TAVILY或SERPAPI
    2. Tavily API (tavily) - 专业AI搜索
    3. SerpApi (serpapi) - 传统Google搜索
    """
    
    def __init__(self,backend: str="hybrid",tavily_key: Optional[str]=None, serpapi_key: Optional[str] = None):
        super().__init__(
            name="search",
            description="一个智能网页搜索引擎。支持混合搜索模式，自动选择最佳搜索源。"
        )
        self.backend = backend
        self.tavily_key = tavily_key or os.getenv("TAVILY_KEY")
        self.serpapi_key = serpapi_key or os.getenv("SERPAPI_API_KEY")
        self.available_backends = []
        # TODO 待完成
        self._setup_backends()
        
    def _setup_backends(self):
        if self.tavily_key:
            try:
                from tavily import TavilyClient
                self.tavily_client = TavilyClient(api_key=self.tavily_key)
                self.available_backends .append("tavily")
                print("✅️ Tavily搜索源已启用")
            except ImportError:
                print(f"⚠️ Tavily库未安装")
        
        if self.serpapi_key:
            try:
                import serpapi
                self.available_backends.append("serpapi")
                print("✅️ SerpApi搜索源已启用")
            except ImportError:
                print(f"⚠️ SerpApi库未安装")
                
        if self.available_backends:
            print(f"🔧 可用搜索源: {','.join(self.available_backends)}")
        else:
            print("⚠️ 没有可用的搜索员")
    
    def run(self, parameters: Dict[str, Any]) -> str:
        """
        执行搜索

        Args:
            parameters: 包含input参数的字典

        Returns:
            搜索结果
        """
        query = parameters.get("input", "").strip()
        if not query:
            return "错误：搜索查询不能为空"

        print(f"🔍 正在执行搜索: {query}")

        try:
            if self.backend == "hybrid":
                return self._search_hybrid(query)
            elif self.backend == "tavily":
                if "tavily" not in self.available_backends:
                    return self._get_api_config_message()
                return self._search_tavily(query)
            elif self.backend == "serpapi":
                if "serpapi" not in self.available_backends:
                    return self._get_api_config_message()
                return self._search_serpapi(query)
            else:
                return self._get_api_config_message()
        except Exception as e:
            return f"搜索时发生错误: {str(e)}"

    def search(self,query:str) -> str:
        if not query.strip():
            return "❌️ 错误: 搜索查询不能为空"
        if not self.available_backends:
            return """❌️ 没有可用的搜索源，请配置以下API密钥之一: 
            1. Tavily API: 设置环境变量 TAVILY_API_KEY
                获取地址: https://tavily.com/
            
            2. SerpAPI: 设置环境变量 SERPAPI_API_KEY 
                获取地址: https://serpapi.com/
                
            配置后请重新运行程序
            """
        print(f"🔍 开始智能搜索: {query}")
        
        # 尝试多个搜索源，返回最佳结果
        for source in self.available_backends:
            try:
                if source == "tavily":
                    result = self._search_tavily(query)
                    if result and "未找到" not in result:
                        return f"📊 Tavily AI搜索结果:\n\n{result}"
                elif source == "serpapi":
                    if result and "未找到" not in result:
                        return f"🌐 SerpApi Google搜索结果:\n\n{result}"
            except Exception as e:
                print(f"⚠️ {source} 搜索失败: {e}")
                continue
            
        return "❌ 所有搜索源都失败了，请检查网络连接和API密钥配置"
    

        
    def _search_hybrid(self, query:str) -> str:
        if "tavily" in self.available_backends:
            try:
                return self._search_tavily(query)
            except Exception as e:
                print(f"⚠️ Tavily搜索失败: {e}")
                # 如果Tavily失败，尝试SerpApi
                if "serpapi" in self.available_backends:
                    print("🔄 切换到SerpApi搜索")
                    return self._search_serpapi(query)
        elif "serapi" in self.available_backends:
            try:
                return self._search_serpapi(query)
            except Exception as e:
                print(f"⚠️ SerpApi搜索失败: {e}")
        
        return "❌️ 没有可用的搜索源，请配置TAVILY_API_KEY 或 SERPAPI_API_KEY环境变量"
        
    def _search_tavily(self,query: str) -> str:
        # TODO 待初始化
        response = self.tavily_client.search(
            query=query,
            search_depth="basic",
            include_answer=True,
            max_results=3,
        )

        result = f"🎯 Tavily AI搜索结果:{response.get('answer', '未找到直接答案')}\n\n"
        
        for i,item in enumerate(response.get("results",[])[:3],1):
            result += f"[{i}] {item.get('title', '')}\n"
            result += f"    {item.get('content', '')[:200]}...\n"
            result += f"    来源: {item.get('url', '')}\n\n"       
        
        return result
    
    def _search_serpapi(self,query: str) -> str:
        import serpapi
        search = serpapi.GoogleSearch({
            "q": query,
            "api_key": self.serpapi_key,
            "num": 3
        })
        
        result = search.get_dict()
        if "organic_results" in result:
            for i, res in enumerate(result["organic_results"][:3],1):
                result += f"[{i}] {res.get("title","")}\n"
                result += f"      {res.get("snippet","")}\n\n"
                
        return result

        
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "input": {"type": "string", "description": "搜索查询"},
            "backend": {"type": "string", "description": "搜索后端类型", "default": "hybrid"}
        }
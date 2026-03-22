import os
from dotenv import load_dotenv
from openai import OpenAI
from typing import List, Dict,Optional

# 加载配置
load_dotenv()

class HelloAgentsLLM:
    def __init__(
            self,
            model: Optional[str] = None,
            apiKey: Optional[str] = None,
            baseUrl: Optional[str] = None,
            provider: Optional[str] = "auto",
            **kwargs
    ):
        # print("正在使用自定义的 ModelScope Provider")
        self.provider = "modelscope"
        
        # 解析 ModelScope 的凭证
        self.api_key = apiKey or os.getenv("ALBAILIAN_API_KEY")
        self.base_url = baseUrl or os.getenv("ALBAILIAN_BASE_URL")
        
        # 验证凭证是否存在
        if not self.api_key:
            raise ValueError("ModelScpoe API key not found. Please set MODELSCOPE_API_KEY environment variable.")
        
        # 设置默认模型和其他参数
        self.model = model or os.getenv("MODEL")
        self.temperature = kwargs.get("temperature", 0.7)
        self.max_tokens = kwargs.get('max_tokens')
        self.timeout = kwargs.get('timeout', 60)
        
        # 使用获得参数创建 OpenAI 客户端实例
        self.client = OpenAI(api_key=self.api_key,base_url=self.base_url,timeout=self.timeout)

    def think(self, messages: List[Dict[str,str]], temperature: float= 0) -> str:
        print(f"正在调 {self.model} 模型...")
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                stream=True,
                timeout= 30,
            )
            
            # 处理响应
            print("✅️ 大语言模型响应成功：")
            collected_content = []
            for chunk in response:
                content = chunk.choices[0].delta.content or ""
                print(content, end="", flush=True)
                collected_content.append(content)
            print()
            return "".join(collected_content)
        
        except Exception as e:
            print(f"❌️ 调用LLM API时发生错误：{e}")
            return None
        
    # def invoke(self, messages: list[dict[str, str]], **kwargs) -> str:
    #     """
    #     非流式调用LLM，返回完整响应。
    #     适用于不需要流式输出的场景。
    #     """
    #     try:
    #         response = self._client.chat.completions.create(
    #             model=self.model,
    #             messages=messages,
    #             temperature=kwargs.get('temperature', self.temperature),
    #             max_tokens=kwargs.get('max_tokens', self.max_tokens),
    #             **{k: v for k, v in kwargs.items() if k not in ['temperature', 'max_tokens']}
    #         )
    #         return response.choices[0].message.content
    #     except Exception as e:
    #         raise HelloAgentsException(f"LLM调用失败: {str(e)}")

    # def stream_invoke(self, messages: list[dict[str, str]], **kwargs) -> Iterator[str]:
    #     """
    #     流式调用LLM的别名方法，与think方法功能相同。
    #     保持向后兼容性。
    #     """
    #     temperature = kwargs.get('temperature')
    #     yield from self.think(messages, temperature)    
    
    
if __name__ == "__main__":
    try:
        llmClient = HelloAgentsLLM()
        
        exampleMessage = [
            {"role": "system", "content": "you are helpful assistant that writes Python code."},
            {"role": "user", "content": "写出一个快速排序算法"},
        ]
        
        print(f"---------调用LLM-------------")
        res = llmClient.think(messages=exampleMessage)
        if res :
            print("\n\n ----------- 完整模型响应 ------------")
            print(res)
    except ValueError as e :
        print(e)
from openai import OpenAI

class OpenAICompatiblaClient:
    def __init__(self,model:str,api_key: str,base_url: str):
        self.model = model
        self.client = OpenAI(api_key=api_key, base_url=base_url)
    
    def generate(self,prompt:str,system_prompt:str) -> str:
        print("正在调用大模型...")
        
        try:
            messages = [
                {'role': 'system','content': system_prompt},
                {'role': 'user', 'content': prompt}
            ]

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=False
            )
            
            answer = response.choices[0].message.content
            print(f"LLM 响应成功!")
            return answer
        except Exception as e:
            print(f"调用 LLM API 时发生错误：{e}")
            return "错误：调用语言模型服务时出错。"


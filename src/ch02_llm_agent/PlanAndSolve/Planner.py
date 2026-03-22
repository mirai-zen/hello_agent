import ast

from .prompt import PLANNER_PROMPT_TEMPLATE
# from ch02_llm_agent.hello_agents_llm import HelloAgentsLLM
from ch02_llm_agent.hello_agents_llm import HelloAgentsLLM
# 规划器
class Planner:
    def __init__(self,llm_client: HelloAgentsLLM):
        self.llm_clinet = llm_client
        
    def plan(self,question: str) -> list[str]:
        prompt = PLANNER_PROMPT_TEMPLATE.format(question=question)
        
        messages = [{"role": "user", "content": prompt}]
        
        print("------- 正在生成计划 ---------")
        
        res_text = self.llm_clinet.think(messages=messages) or ""
        print(f"✅️ 计划已生成: \n{res_text}")
        
        # 解析 LLM 输出的列表字符串
        try:
            plan_str = res_text.split("```python")[1].split("```")[0].strip()
            # 使用ast.literal_eval 来安全地执行字符串，将其转换为 Python 列表
            plan = ast.literal_eval(plan_str)
            return plan if isinstance(plan,list) else []
        except (ValueError,SyntaxError,IndexError) as e:
            print(f"❌️ 解析计划时出错：{e}")
            print(f"原始响应：{res_text}")
            return []
        except Exception as e:
            print(f"❌️ 解析计划时发生未知错误: {e}")
            return []

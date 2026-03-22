from .prompt import EXECUTOR_PROMPT_TEMPLATE
from ch02_llm_agent.hello_agents_llm import HelloAgentsLLM
class Executor:
    def __init__(self,llm_client: HelloAgentsLLM):
        # self.client = llm_client
        self.llm_client = llm_client
        
    def execute(self, question: str, plan: list[str]) -> str:
        history = "" # 用于存储历史步骤和结果的字符串
        print("\n-------- 正在执行计划 -----------")
        
        
        for i, step in enumerate(plan):
            print(f"\n -> 正在执行步骤 {i + 1}/ {len(plan)}:{step}")
            
            prompt = EXECUTOR_PROMPT_TEMPLATE.format(
                question=question,
                plan=plan,
                history=history,
                current_step=step
            )
            
            messages = [{"role": "user","content": prompt}]
            
            # res_text = self.client.think(messages) or ""
            res_text = self.llm_client.think(messages) or ""
            
            # 更新历史
            history += f"步骤 {i+1}: {step}\n结果: {res_text}\n\n"
            print(f"步骤 {i+1} 已完成, 结果：{res_text}")
            
        final_answer = res_text
        return final_answer
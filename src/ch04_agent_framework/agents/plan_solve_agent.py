import ast
from ..core import Agent, HelloAgentsLLM,Config
from typing import List, Optional


class PlanSolveAgent(Agent):
    def __init__(
        self, 
        name: str, 
        llm: HelloAgentsLLM, 
        system_prompt: Optional[str] = None, 
        config: Optional[Config] = None,
    ):
        super().__init__(name, llm, system_prompt, config)
        self.current_history:List[str] = []
        self.planner = Planner(self.llm)
        self.executor = Executor(self.llm)
             
    def run(self,question: str) -> str:
        print(f"\n ---- 开始处理问题 ----\n问题: {question}")
        
        # 1. 调用规划期生成计划
        plan = self.planner.plan(question)
        if not plan:
            print(f"\n ---- 任务终止 ---- \n 无法生成有效的行动计划")
            return 

        # 2. 调用执行器执行计划
        final_answer = self.executor.execute(question,plan)
        return final_answer

# 规划器
class Planner:
    def __init__(self,llm: HelloAgentsLLM):
        self.llm = llm
        
    def plan(self,question: str) -> list[str]:
        prompt = DEFAULT_PLANNER_PROMPT.format(question=question)
        
        messages = [{"role": "user", "content": prompt}]
        
        print("------- 正在生成计划 ---------")
        
        res_text = self.llm.invoke(messages=messages) or ""
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




# 执行器
class Executor:
    def __init__(self,llm_client: HelloAgentsLLM):
        self.llm_client = llm_client
        
    def execute(self, question: str, plan: list[str]) -> str:
        history = "" # 用于存储历史步骤和结果的字符串
        print("\n-------- 正在执行计划 -----------")
        
        
        for i, step in enumerate(plan):
            print(f"\n -> 正在执行步骤 {i + 1}/ {len(plan)}:{step}")
            
            prompt = DEFAULT_EXECUTOR_PROMPT.format(
                question=question,
                plan=plan,
                history=history,
                current_step=step
            )
            
            messages = [{"role": "user","content": prompt}]
            
            # res_text = self.client.think(messages) or ""
            res_text = self.llm_client.invoke(messages) or ""
            
            # 更新历史
            history += f"步骤 {i+1}: {step}\n结果: {res_text}\n\n"
            print(f"步骤 {i+1} 已完成, 结果：{res_text}")
            
        final_answer = res_text
        return final_answer


        


# 默认规划器提示词模板
DEFAULT_PLANNER_PROMPT = """
你是一个顶级的AI规划专家。你的任务是将用户提出的复杂问题分解成一个由多个简单步骤组成的行动计划。
请确保计划中的每个步骤都是一个独立的、可执行的子任务，并且严格按照逻辑顺序排列。
你的输出必须是一个Python列表，其中每个元素都是一个描述子任务的字符串。

问题: {question}

请严格按照以下格式输出你的计划:
```python
["步骤1", "步骤2", "步骤3", ...]
```
"""

# 默认执行器提示词模板
DEFAULT_EXECUTOR_PROMPT = """
你是一位顶级的AI执行专家。你的任务是严格按照给定的计划，一步步地解决问题。
你将收到原始问题、完整的计划、以及到目前为止已经完成的步骤和结果。
请你专注于解决"当前步骤"，并仅输出该步骤的最终答案，不要输出任何额外的解释或对话。

# 原始问题:
{question}

# 完整计划:
{plan}

# 历史步骤与结果:
{history}

# 当前步骤:
{current_step}

请仅输出针对"当前步骤"的回答:
"""
DEFAULT_PROMPTS = {
    "initial": """
请根据以下要求完成任务:

任务: {task}

请提供一个完整、准确的回答。
""",
    "reflect": """
请仔细审查以下回答，并找出可能的问题或改进空间:

# 原始任务:
{task}

# 当前回答:
{content}

请分析这个回答的质量，指出不足之处，并提出具体的改进建议。
如果回答已经很好，请回答"无需改进"。
""",
    "refine": """
请根据反馈意见改进你的回答:

# 原始任务:
{task}

# 上一轮回答:
{last_attempt}

# 反馈意见:
{feedback}

请提供一个改进后的回答。
"""
}
from typing import Optional,Dict

from ..core import HelloAgentsLLM,Agent,Config

class ReflectionAgent(Agent):
    def __init__(
            self, 
            name: str, 
            llm: HelloAgentsLLM, 
            system_prompt: Optional[str] = None, 
            config: Optional[Config] = None,
            max_steps: int = 5,
            custom_prompts: Dict = None,
            max_iterations: int = 5
        ):
        super().__init__(name, llm, system_prompt, config)
        self.memory = Memory()
        self.coustom_prompts = custom_prompts or DEFAULT_PROMPTS
        self.max_iterations = max_iterations
        
    def run(self,task:str):
        print(f"\n ---  开始处理任务 --- \n 任务：{task}")
        
        # 1. 初始执行
        print("\n --- 正在执行初始尝试 ---")
        initial_prompt = self.coustom_prompts["initial"].format(task=task)
        initial_code = self.__get_llm_response(initial_prompt)
        self.memory.add_record("execution", initial_code)
        
        # 2. 迭代循环： 反思与优化
        for i in range(self.max_iterations):
            print(f"\n --- 第 {i + 1}/{self.max_iterations} 轮迭代 ---")
            
            # a 反思
            print("\n -> 正在进行反思...")
            last_code = self.memory.get_last_execution()
            reflect_prompt = self.coustom_prompts["reflect"].format(task=task, content=last_code)
            feedback = self.__get_llm_response(reflect_prompt)
            self.memory.add_record("reflection", feedback)
            
            # b. 检查是否需要停止更新
            if "无需改进" in feedback:
                print(f"\n ✅️ 反思认为代码已无需改进，任务完成。")
                break
            
            # c. 优化
            print("\n -> 正在进行优化...")
            refine_prompt = self.coustom_prompts['refine'].format(
                task=task,
                last_attempt=last_code,
                feedback=feedback
            )
            refine_code = self.__get_llm_response(refine_prompt)
            self.memory.add_record("exection", refine_code)
            
        final_code = self.memory.get_last_execution()
        print(f"\n ---- 任务完成 ---- \n 最终生成的代码：\n ```python\n{final_code}\n```")
        return final_code
            
        


    def __get_llm_response(self, prompt: str) -> str:
        messages = [{"role": "user", "content": prompt}]
        res_text = self.llm.think(messages) or ""
        return res_text


"""
一个简单的短期记忆模块，用于存储智能体的行动与反思轨迹。
"""
from typing import List, Dict, Any, Optional

class Memory:
    def __init__(self):
        self.records: List[Dict[str,Any]] = []
    
    def add_record(self,record_type: str, content: str):
        record = {"type": record_type,  "content": content}
        self.records.append(record)
        print(f"📝 记忆已更新，新增一条 '{record_type}' 记录")
        
    def get_trajectory(self) -> str:
        trajectory_parts = []
        
        for record in self.records:
            if record['type'] == 'exection':
                trajectory_parts.append(f"---- 上一轮尝试（代码）-----\n{record['content']}")
            elif record['type'] == 'reflection':
                trajectory_parts.append(f"---- 评审员反馈 -----\n{record['content']}")
                
        return "\n\n".join(trajectory_parts)
    
    def get_last_execution(self) -> Optional[str]:
        for record in reversed(self.records):
            if record['type'] == 'execution':
                return record['content']
        return None
    


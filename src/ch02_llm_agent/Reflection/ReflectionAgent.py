from dotenv import load_dotenv

from ch02_llm_agent.hello_agents_llm import HelloAgentsLLM
from ch02_llm_agent.Reflection.Memory import Memory
from ch02_llm_agent.Reflection.prompt import INITAL_PROMPT_TEMPLATE,REFINE_PROMPT_TEMPLATE,REFLECT_PROMPT_TEMPLATE

class ReflectionAgent:
    def __init__(self,llm_client: HelloAgentsLLM,max_iterations = 3):
        self.llm_client = llm_client
        self.memory = Memory()
        self.max_iterations = max_iterations
        
    def run(self,task:str):
        print(f"\n ---  开始处理任务 --- \n 任务：{task}")
        
        # 1. 初始执行
        print("\n --- 正在执行初始尝试 ---")
        initial_prompt = INITAL_PROMPT_TEMPLATE.format(task=task)
        initial_code = self.__get_llm_response(initial_prompt)
        self.memory.add_record("execution", initial_code)
        
        # 2. 迭代循环： 反思与优化
        for i in range(self.max_iterations):
            print(f"\n --- 第 {i + 1}/{self.max_iterations} 轮迭代 ---")
            
            # a 反思
            print("\n -> 正在进行反思...")
            last_code = self.memory.get_last_execution()
            reflect_prompt = REFLECT_PROMPT_TEMPLATE.format(task=task,code=last_code)
            feedback = self.__get_llm_response(reflect_prompt)
            self.memory.add_record("reflection", feedback)
            
            # b. 检查是否需要停止更新
            if "无需改进" in feedback:
                print(f"\n ✅️ 反思认为代码已无需改进，任务完成。")
                break
            
            # c. 优化
            print("\n -> 正在进行优化...")
            refine_prompt = REFINE_PROMPT_TEMPLATE.format(
                task=task,
                last_code_attempt=last_code,
                feedback=feedback
            )
            refine_code = self.__get_llm_response(refine_prompt)
            self.memory.add_record("exection", refine_code)
            
        final_code = self.memory.get_last_execution()
        print(f"\n ---- 任务完成 ---- \n 最终生成的代码：\n ```python\n{final_code}\n```")
        return final_code
            
        


    def __get_llm_response(self, prompt: str) -> str:
        messages = [{"role": "user", "content": prompt}]
        res_text = self.llm_client.think(messages) or ""
        return res_text
    


if __name__ == "__main__":
    load_dotenv()
    llmClient = HelloAgentsLLM()
    
    agent = ReflectionAgent(llm_client=llmClient)
    agent.run("编写一个Python函数，找出1到n之间所有的素数 (prime numbers)。")
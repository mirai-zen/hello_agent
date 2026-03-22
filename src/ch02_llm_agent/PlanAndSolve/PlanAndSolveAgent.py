from dotenv import load_dotenv
from openai import OpenAI

# PlanAndSolveAgent.py 里
from ch02_llm_agent.PlanAndSolve.Planner import Planner
from ch02_llm_agent.PlanAndSolve.Executor import Executor
from ch02_llm_agent.hello_agents_llm import HelloAgentsLLM

class PlanAndSolve:
    def __init__(self, llm_client):
        self.client = llm_client
        self.planner = Planner(self.client)
        self.executor = Executor(self.client)
        
    def run(self,question: str):
        print(f"\n ---- 开始处理问题 ----\n问题: {question}")
        
        # 1. 调用规划期生成计划
        plan = self.planner.plan(question)
        if not plan:
            print(f"\n ---- 任务终止 ---- \n 无法生成有效的行动计划")
            return 

        # 2. 调用执行器执行计划
        final_answer = self.executor.execute(question,plan)
        print(f'\n ----- 任务完成 ----- \n最终答案： {final_answer}')
        

if __name__ == "__main__":
    load_dotenv()
    llmClient = HelloAgentsLLM()

 
    agent = PlanAndSolve(llm_client=llmClient)
    
    agent.run("一个水果店周一卖出了15个苹果。周二卖出的苹果数量是周一的两倍。周三卖出的数量比周二少了5个。请问这三天总共卖出了多少个苹果？")
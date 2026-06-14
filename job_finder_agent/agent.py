from google.adk.tools import google_search
from google.adk.agents import Agent, ParallelAgent, SequentialAgent
from dotenv import load_dotenv

load_dotenv()

# Specialist Agent 1
linkedin_finder_agent = Agent(
    name="linkedin_finder_agent", model="gemini-2.5-flash", tools=[google_search],
    instruction="You are a LinkedIn expert. Find the Salesforce marketing cloud specialist jobs and Salesforce data cloud job based on the user's query. Output will be a list of job titles ,email id ,contact person ,weburl and company names.",
    output_key="linkedin_result"
)

# Specialist Agent 2
naukri_finder_agent = Agent(
    name="naukri_finder_agent", model="gemini-2.5-flash", tools=[google_search],
    instruction="You are a job search expert.  Find the Salesforce marketing cloud specialist jobs and Salesforce data cloud job based on the user's query. Output will be a list of job titles ,email id ,contact person ,weburl and company names.",
    output_key="naukri_result"
)

# We can reuse our company_portal_job_agent for the third parallel task!
# Just need to give it a new output_key for this workflow.
# company_portal_job_agent = company_portal_job_agent.copy(update={"output_key": "restaurant_result"})
company_portal_job_agent = Agent(
    name="company_portal_job_agent",
    model="gemini-2.5-flash",
    tools=[google_search],
    instruction="""You are an expert in finding job opportunities. Your goal is to visit IT companies web portals and find Salesforce marketing cloud specialist jobs and Salesforce data cloud jobs based on a user's request.

    Output will be a list of job titles ,email id ,contact person ,weburl and company names.    
    """,
    output_key="job_portal_result" # Set the correct output key for this workflow
)


# ✨ The ParallelAgent runs all three specialists at once ✨
parallel_job_search_agent = ParallelAgent(
    name="parallel_job_search_agent",
    sub_agents=[linkedin_finder_agent, naukri_finder_agent, company_portal_job_agent]
)

# Agent to synthesize the parallel results
synthesis_agent = Agent(
    name="synthesis_agent", model="gemini-2.5-flash",
    instruction="""You are a helpful assistant. Combine the following research results into a clear, bulleted list for the user.
    - Linkedin: {linkedin_result}
    - Naukri: {naukri_result}
    - Job Portals: {job_portal_result}
    """
)

# ✨ The SequentialAgent runs the parallel search, then the synthesis ✨
parallel_planner_agent = SequentialAgent(
    name="parallel_planner_agent",
    sub_agents=[parallel_job_search_agent, synthesis_agent],
    description="A workflow that finds multiple things in parallel and then summarizes the results."
)

root_agent = parallel_planner_agent
print("🤖 Agent team supercharged with a ParallelAgent workflow!")
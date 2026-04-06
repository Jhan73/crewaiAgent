from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai_tools import SerperDevTool, DOCXSearchTool
from .tools.notion_tool import NotionTool

# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class YouTubeScript():
    """YouTubeScript crew"""

    agents: list[BaseAgent]
    tasks: list[Task]

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def youtuber_manager(self) -> Agent:
        return Agent(
            config=self.agents_config['youtuber_manager'], # type: ignore[index]
            verbose=True
        )

    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['researcher'], # type: ignore[index]
            verbose=True,
            tools=[
                SerperDevTool()
            ]
        )

    @agent
    def screenwriter(self) -> Agent:
        return Agent(
            config=self.agents_config['screenwriter'], # type: ignore[index]
            verbose=True,
            tools=[
                DOCXSearchTool(directory='/knowledge/script_template.docx'),
                NotionTool()
            ]
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_task'], # type: ignore[index]
        )

    @task
    def screenwriting_task(self) -> Task:
        return Task(
            config=self.tasks_config['screenwriting_task'], # type: ignore[index]
            dependencies=[self.research_task], # This means that the screenwriting_task will only start once the research_task is completed
        )

    @crew
    def crew(self) -> Crew:
        """Creates the CrewProject crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        manager = self.youtuber_manager()
        agents = [agent for agent in self.agents if agent is not manager]

        return Crew(
            agents=agents,
            tasks=self.tasks,
            process=Process.hierarchical,
            manager_agent=manager,
            verbose=True,
        )

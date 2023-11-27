from langchain.agents import AgentType, initialize_agent
from langchain.chains import (ConversationalRetrievalChain,
                              RetrievalQAWithSourcesChain)
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferMemory
from langchain.tools import Tool, WikipediaQueryRun
from langchain.utilities import WikipediaAPIWrapper


class WebLLM:
    def __init__(self, web_vector_store):
        vector_store = web_vector_store.faiss

        self.llm = OpenAI(temperature=0.2)
        self.memory = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True
        )
        self.llm_tools = get_agent_tools(self.llm, vector_store, self.memory)

        self.agent = initialize_agent(
            self.llm_tools,
            self.llm,
            agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
            memory=self.memory,
            verbose=True,
        )

    def query(self, query):
        response = self.agent.run(query)
        return response
    
    def reset_memory(self):
        self.agent.memory.clear()
        for tool in self.llm_tools:
            print("Tool type", type(tool))


def get_agent_tools(llm, vector_store, memory):
    qa_conversation = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vector_store.as_retriever(search_kwargs={"k": 5}),
        memory=memory,
    )

    qa_sources = RetrievalQAWithSourcesChain.from_llm(
        llm=llm,
        retriever=vector_store.as_retriever(search_kwargs={"k": 5}),
    )

    wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())

    tools = [
        Tool(
            name="QA Sources",
            func=qa_sources,
            description="Answers questions when it seems like returning\
                the resource link is useful",
        ),
        Tool(
            name="QA Conversation",
            func=qa_conversation.run,
            description="Best tool. Conversational agent that answers questions.",
            return_direct=True,
        ),
        Tool(
            name="Wikipedia Query",
            func=wikipedia.run,
            description="Only use this if you can't find the answer in other tools",
        ),
    ]

    return tools


if __name__ == "__main__":
    pass

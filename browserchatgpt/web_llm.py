# from langchain.chains import (ConversationalRetrievalChain,
#                               RetrievalQAWithSourcesChain)
# from langchain.llms import OpenAI
# from langchain.memory import ConversationBufferMemory


# class WebLLM:
#     def __init__(self, web_vector_store):
#         vector_store = web_vector_store.faiss
#         memory = ConversationBufferMemory(
#             memory_key="chat_history", return_messages=True
#         )

#         llm = OpenAI(temperature=0.2)
#         # llm = OpenAI(temperature=0, model_name="gpt-3.5-instruct")

#         self.qa = RetrievalQAWithSourcesChain.from_llm(
#             llm=llm, retriever=vector_store.as_retriever(search_kwargs={"k": 5})
#         )
#         # self.qa = ConversationalRetrievalChain.from_llm(
#         #    llm=llm,
#         #    retriever=vector_store.as_retriever(search_kwargs={"k": 5}),
#         #    memory=memory,
#         # )

#     def query(self, query):
#         result = self.qa({"question": query})

#         # used for retrievalwithsources
#         answer, sources = result["answer"], result["sources"]

#         sources_list = [source.strip() for source in sources.split(",")]
#         print(f"Response sources {sources_list}")
#         response = "".join((answer, sources_list[0]))

#         # response = result["answer"]

#         return response


# if __name__ == "__main__":
#     pass
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

        self.agent_executer = initialize_agent(
            self.llm_tools,
            self.llm,
            #agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,     # Can't converse nor return links
            agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION, # Can converse and do links but too many hallucinations
            memory=self.memory,
            verbose=True,
        )
        

        current_prompt = self.agent_executer.agent.llm_chain.prompt.template
        new_prompt = update_prompt(current_prompt)
        self.agent_executer.agent.llm_chain.prompt.template = new_prompt
        #print(self.agent_executer.agent.llm_chain.prompt.template)

    def query(self, query):
        response = self.agent_executer.run(query)
        #print(self.agent_executer.agent.llm_chain.prompt.template)

        return response

    def reset_memory(self):
        self.agent_executer.memory.clear()


def get_agent_tools(llm, vector_store, memory):
    qa_conversation = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vector_store.as_retriever(search_kwargs={"k": 4}),
        memory=memory,
    )

    qa_sources = RetrievalQAWithSourcesChain.from_llm(
        llm=llm,
        retriever=vector_store.as_retriever(search_kwargs={"k": 4})
    )

    wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())

    tools = [
        Tool(
            name="QA Conversation",
            func=qa_conversation.run,
            return_direct=True,
            description="Best tool. Always use this first. Answers "
            "questions and is able to hold a conversation as well.",
        ),
        Tool(
            name="QA Sources",
            func=qa_sources,
            description="Answers questions when a source for "
            "the answer is needed such as a link or url.",
        ),
        Tool(
            name="Wikipedia Query",
            func=wikipedia.run,
            description="Only use this tool when the other tools "
            "fail to return an answer.",
        ),
    ]

    return tools


def update_prompt(prompt):
    """Only used with AgentType.CONVERSATIONAL_REACT_DESCRIPTION."""
    sub_str = "To use a tool"
    additional_str = (
        "After every new_input you must always use a tool"
        "\nIf that tool doesn't contain an answer "
        "only then can you respond without a tool.\n\n"
    )

    index = prompt.find(sub_str)
    if index != -1:
        modified_string = prompt[:index] + additional_str + prompt[index:]
    else:
        print("Substring not found")


    sub_str = "When you have a response"
    additional_str = (
        "You are not allowed to respond without a tool after a new_input\n"
        "If the tool was unable to find the answer, let the user know.\n"
        "Don't answer any questions that don't have answers in one of the tools.\n"
    )

    index = modified_string.find(sub_str)
    if index != -1:
        modified_string = (
            modified_string[:index] + additional_str + modified_string[index:]
        )
    else:
        print("Substring not found")


    return modified_string


if __name__ == "__main__":
    pass
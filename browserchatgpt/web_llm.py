# Import necessary modules and classes from the langchain library
from langchain.agents import AgentType, initialize_agent
from langchain.chains import (ConversationalRetrievalChain,
                              RetrievalQAWithSourcesChain)
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferMemory
from langchain.tools import Tool, WikipediaQueryRun
from langchain.utilities import WikipediaAPIWrapper

# Define a class called WebLLM
class WebLLM:
    def __init__(self, web_vector_store):
        # Initialize the WebLLM instance with a Faiss vector store
        vector_store = web_vector_store.faiss

        # Initialize the OpenAI language model with a temperature of 0.2
        self.llm = OpenAI(temperature=0.2)

        # Create a ConversationBufferMemory instance for storing conversation history
        self.memory = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True
        )

        # Get tools for the language model
        self.llm_tools = get_agent_tools(self.llm, vector_store, self.memory)

        # Initialize an agent with the specified tools, language model, and memory
        self.agent_executer = initialize_agent(
            self.llm_tools,
            self.llm,
            agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,  # Preferably use constant values for clarity
            memory=self.memory,
            verbose=True,
        )

        # Update the prompt template for the agent
        current_prompt = self.agent_executer.agent.llm_chain.prompt.template
        new_prompt = update_prompt(current_prompt)
        self.agent_executer.agent.llm_chain.prompt.template = new_prompt

    # Method for querying the language model
    def query(self, query):
        response = self.agent_executer.run(query)

        return response

    # Method for resetting conversation memory
    def reset_memory(self):
        self.agent_executer.memory.clear()

# Function to get a list of tools for the language model
def get_agent_tools(llm, vector_store, memory):
    # Define two chains for different purposes
    qa_conversation = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vector_store.as_retriever(search_kwargs={"k": 4}),
        memory=memory,
    )
    qa_sources = RetrievalQAWithSourcesChain.from_llm(
        llm=llm,
        retriever=vector_store.as_retriever(search_kwargs={"k": 4})
    )

    # Create a tool list with different functionalities
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
            func=WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper()).run,
            description="Only use this tool when the other tools "
                        "fail to return an answer.",
        ),
    ]

    return tools

# Function to update the prompt template for a conversational agent
def update_prompt(prompt):
    # Add additional instructions to the prompt
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

# Entry point to the script
if __name__ == "__main__":
    pass  # Placeholder, script does nothing when executed directly

from langchain.chains import (ConversationalRetrievalChain, RetrievalQA,
                              RetrievalQAWithSourcesChain,
                              VectorDBQAWithSourcesChain)
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferMemory


class WebLLM:
    def __init__(self, web_data):
        vector_store = web_data.vector_store
        memory = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True
        )

        # self.qa = RetrievalQAWithSourcesChain.from_llm(llm=OpenAI(temperature=0),
        #                                              vectorstore=vector_store,
        #                                              memory=memory)

        self.qa = ConversationalRetrievalChain.from_llm(
            llm=OpenAI(model="gpt-3.5-turbo-instruct", temperature=0),
            retriever=vector_store.as_retriever(search_kwargs={"k": 5}),
            memory=memory,
        )

    def query(self, query):
        result = self.qa({"question": query})
        return result["answer"]


if __name__ == "__main__":
    pass

from langchain.chains import (ConversationalRetrievalChain,
                              RetrievalQAWithSourcesChain)
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferMemory


class WebLLM:
    def __init__(self, web_vector_store):
        vector_store = web_vector_store.faiss
        memory = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True
        )

        llm = OpenAI(temperature=0.2)
        # llm = OpenAI(temperature=0, model_name="gpt-3.5-instruct")

        self.qa = RetrievalQAWithSourcesChain.from_llm(
            llm=llm, retriever=vector_store.as_retriever(search_kwargs={"k": 5})
        )
        # self.qa = ConversationalRetrievalChain.from_llm(
        #    llm=llm,
        #    retriever=vector_store.as_retriever(search_kwargs={"k": 5}),
        #    memory=memory,
        # )

    def query(self, query):
        result = self.qa({"question": query})

        # used for retrievalwithsources
        answer, sources = result["answer"], result["sources"]

        sources_list = [source.strip() for source in sources.split(",")]
        print(f"Response sources {sources_list}")
        response = "".join((answer, sources_list[0]))

        # response = result["answer"]

        return response


if __name__ == "__main__":
    pass

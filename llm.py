from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA


def generate_response(question, gpt_model, openai_api_key):
    llm = ChatOpenAI(model=gpt_model, temperature=0.7, openai_api_key=openai_api_key)
    output = llm.invoke(question)
    output_parser = StrOutputParser()
    output = output_parser.invoke(output)
    return output


# qa_chain
def get_qa_chain(question, gpt_model, openai_api_key, vectordb):
    llm = ChatOpenAI(model_name=gpt_model, temperature=0, openai_api_key=openai_api_key)

    template = """
    Use the following context to answer the final question. If you don't know the answer, just say you don't know and don't try to make up an answer. Use at most three sentences. Try to keep the answer concise. Always end your response with 'Thank you for your question!'
    {context}
    Question: {question}
    """
    QA_CHAIN_PROMPT = PromptTemplate(
        input_variables=["context", "question"], template=template
    )
    qa_chain = RetrievalQA.from_chain_type(
        llm,
        retriever=vectordb.as_retriever(),
        return_source_documents=True,
        chain_type_kwargs={"prompt": QA_CHAIN_PROMPT},
    )
    result = qa_chain({"query": question})
    return result["result"]


# qa_chain with history
def get_chat_qa_chain(question, gpt_model, openai_api_key, vectordb):
    llm = ChatOpenAI(model_name=gpt_model, temperature=0, openai_api_key=openai_api_key)

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
    )
    retriever = vectordb.as_retriever()
    qa = ConversationalRetrievalChain.from_llm(llm, retriever=retriever, memory=memory)
    result = qa({"question": question})
    return result["answer"]

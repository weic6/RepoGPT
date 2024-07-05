from langchain_openai import OpenAIEmbeddings
import os
import shutil
from crawl import *
from langchain_community.vectorstores.chroma import Chroma


def get_vectordb(
    openai_api_key, owner, repo, github_token=None, persist_directory=None
):
    embedding = OpenAIEmbeddings(openai_api_key=openai_api_key)

    if persist_directory is None:
        persist_directory = "/repo-gpt_persist_test2"

    if os.path.exists(persist_directory):
        shutil.rmtree(persist_directory)  # remove the directory and its contents

    file_paths = crawl_repo(owner, repo, github_token)

    from langchain.docstore.document import Document

    documents = [
        Document(
            page_content=fetch_file_content(owner, repo, path, github_token),
            metadata={"file_path": path},
        )
        for path in file_paths
    ]

    vectordb = Chroma.from_documents(
        documents=documents,
        embedding=embedding,
        persist_directory=persist_directory,
    )
    vectordb.persist()
    return vectordb


def load_vector_db(
    openai_api_key, owner, repo, github_token=None, persist_directory=None
):

    if not os.path.exists(persist_directory):
        print(f"Persist directory {persist_directory} does not exist.")

    embedding = OpenAIEmbeddings(openai_api_key=openai_api_key)
    vectordb = Chroma(
        persist_directory=persist_directory,
        embedding_function=embedding,
    )
    return vectordb

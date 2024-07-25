__import__("pysqlite3")
import sys

# import pysqlite3

sys.modules["sqlite3"] = sys.modules["pysqlite3"]

from langchain_openai import OpenAIEmbeddings
import os
import shutil
from crawl import *
from langchain_community.vectorstores.chroma import Chroma


def get_vectordb(openai_api_key, repo_path, persist_directory=None):
    embedding = OpenAIEmbeddings(openai_api_key=openai_api_key)

    if persist_directory is None:
        persist_directory = os.path.join(repo_path, "_chroma")

    if os.path.exists(persist_directory):
        shutil.rmtree(persist_directory)  # remove the directory and its contents

    file_paths = crawl_local_repo(repo_path)

    from langchain.docstore.document import Document

    documents = [
        Document(
            page_content=read_file_content(path),
            metadata={"source": path},
        )
        for path in file_paths
        if read_file_content(path)
    ]

    vectordb = Chroma.from_documents(
        documents=documents,
        embedding=embedding,
        persist_directory=persist_directory,
    )
    vectordb.persist()
    return vectordb


def load_vector_db(openai_api_key, persist_directory=None):
    if not os.path.exists(persist_directory):
        print(f"Persist directory {persist_directory} does not exist.")
        return None

    embedding = OpenAIEmbeddings(openai_api_key=openai_api_key)
    vectordb = Chroma(
        persist_directory=persist_directory,
        embedding_function=embedding,
    )
    return vectordb

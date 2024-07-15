# RepoGPT

RepoGPT is an intuitive and powerful chatbot, which everages the power of Large Language Model (LLM) and Retrieval-Augmented Generation (RAG) for interacting with GitHub repositories, and assist developer to understand the codes better and faster. This chatboot significantly speeds up the learning curve for secondary application development based on open source repository.

## Overview

The backend uses the GitHub API for retrieving repository documents, the LangChain library to simplify the creation of the chatbot, and the Chroma vector store for managing and querying vectorized content, and OpenAI API to empower interactions with users. The frontend uses Streamlit to create an interactive interface.

Upon receiving the github repository url, RepoGPT will crawl documents inside the repository, and vectorize the content and stored in Chrome, for retrieval-augmented generation. Users can then chat with the repository to get insights and guidance.

## Key Features

- Developed an advanced AI-powered chatbot for analyzing and interacting with GitHub repositories to enhanced secondary application development by providing quick and insightful access to open source codebases.
- Implemented repository crawling using the GitHub API to retrieve files efficiently.
- Leveraged Retrieval-Augmented Generation (RAG) to enable insightful conversations with repository content.
- Utilized Streamlit for the user interface, providing an intuitive and interactive experience for users.
- Integrated Chroma vector store for managing and querying vectorized content from repositories.

## Run guide

Install dependencies.

```python
pip install -r requirement.txt
```

Create .env file and append the followling lines:

```python
OPENAI_API_KEY="xxxxxx"
GITHUB_TOKEN="xxxxxx"
CHROMA_DIR="xxxxxx"

```

Run application.

```python
streamlit run app.py
```

## Todo

- [ ] add a video walkthrough
- [ ] calculate num of token before vectorization
- [ ] incorporate other model (hugging face?)
- [ ] deploy on hugging face?
- [ ] issues, and pull requests
- [ ] crawl Q&As in repository issues, and pull requests (to provide more context to the chatbot and improve the quality of answer)
- [ ] provide more AI models for users to choose from.
- [ ] support the local deployment of chatbot to prevent privacy leaking.

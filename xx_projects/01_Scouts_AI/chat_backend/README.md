# RAG-Based AI Chatbot Application

## Description

This project implements a **Retrieval-Augmented Generation (RAG)**-based AI chatbot that retrieves information from a collection of PDF documents to generate accurate responses to user queries. The chatbot is built using **FastAPI** and integrates with a **vector database** to efficiently store and retrieve document embeddings.

## Features

- PDF document processing and chunking for improved information retrieval.
- Integration with a vector database to store and retrieve document embeddings.
- Combines retrieved document chunks with a language model to generate responses.
- FastAPI-based API for chat interactions.
- Automatic processing of PDFs added to a designated directory.

## Installation

### Prerequisites

- Python 3.10+
- Poetry (for dependency management)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/Harry5174/learning_generative_ai/tree/main/04_llm/01_projects/01_Scouts_AI/chat_backend
   ```

2. Install Depedencies using Poetry:
    ```bash
    poetry install
    ```

4. Add your documents to the `assets/pdfs/` directory

### Usage

To start the application

1. Start the FastAPI server:
    ```bash
    poetry run uvicorn main:app --reload
    ```

2. The application will process the PDFs in assets/pdfs/ and store their chunks in the vector database.

3. You can interact with the chatbot by sending a POST request to the /chat endpoint. For example:
    ```bash
    curl -X 'POST' \
    'http://127.0.0.1:8000/chat' \
    -H 'Content-Type: application/json' \
    -d '{
    "query": "What is a vehicle emergency kit?"
    }'
    ```

### API Reference

- GET /: Health check endpoint to verify the server status.

- POST /chat: Accepts user queries and retrieves responses based on the stored PDF data.


### Contributing
Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a new branch (git checkout -b feature/your-feature).
3. Make your changes and commit them (git commit -am 'Add new feature').
4. Push the branch (git push origin feature/your-feature).
5. Submit a Pull Request for review.


### Authors and Acknowledgment

This project was created by Harry.

### Contact Information

For any questions or suggestions, please contact harisjaved010@gmail.com.
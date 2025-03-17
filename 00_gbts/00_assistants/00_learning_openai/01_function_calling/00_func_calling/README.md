# OpenAI Assistant with Database Interaction

## Description

This project combines the power of OpenAI with FastAPI to create an interactive chat interface. The AI assistant can engage in conversations, and the project is enriched with database integration for storing and retrieving user queries related to persons and their locations. The assistant's functionality is extended through various tools and functions defined in the `functions.py` module.

## Features

- Interactive chat with an AI assistant powered by OpenAI.
- Database integration for managing and retrieving information about persons and their locations.
- Creation of new persons, retrieval of person locations, and listing all persons stored in the database.
- Streamlit web interface for user interaction with the assistant.

## Installation

### Prerequisites

- Python 3.8+
- FastAPI
- SQLModel
- OpenAI
- requests
- Streamlit
- HTTPX

### Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/Harry5174/Generative_AI.git
   cd https://github.com/Harry5174/Generative_AI/tree/main/00_assistants/00_Knowledge_retrievel
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Set up the environment variables:
   - `OPENAI_API_KEY`: Obtain an OpenAI API key and set it in your environment.
   - `DATABASE_URL`: Set the URL for your database.

## Usage

To use the project, follow these steps:

1. Start the FastAPI server:

   ```bash
   uvicorn main:app --reload
   ```

2. Run the Streamlit app:

   ```bash
   streamlit run streamlit_app.py
   ```

3. Access the interactive chat interface and start a new conversation.

## API Reference

The project exposes the following API endpoints:

- `/start`: Initiates a new conversation with the AI assistant.
- `/chat`: Allows users to send messages and receive responses from the assistant.
- `/persons/`: Retrieves data of all persons from the database.
- `/person/`: Creates a new person record in the database.
- `/location/{name}`: Retrieves the location of a person by their name.

## Contributing

Contributions are welcome! Follow these steps to contribute to the project:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/improvement`).
3. Make your changes and commit them (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature/improvement`).
5. Create a new Pull Request.

## Authors and Acknowledgment

This project was created by Harry.

## License

This project is licensed under the [MIT License](LICENSE).

## Contact Information

For questions or suggestions, please contact harisjaved010@gmail.com.

## FAQs

**Q:** How can I customize the responses of the AI assistant?
**A:** You can modify the tools/functions which are defined in `functions.py` to tailor the assistant's behavior to your needs.

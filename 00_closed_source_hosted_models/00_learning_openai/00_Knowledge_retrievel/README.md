# FastAPI OpenAI Assistant

## Description

This project aims to provide an interactive chat interface with an AI assistant powered by OpenAI. Users can engage in conversations with the assistant, which can provide customizable responses based on user input. The project also integrates with a database for storing and retrieving user queries, enhancing the assistant's capabilities.

## Features

- Interactive chat with an AI assistant.
- Database integration for storing and retrieving user queries.
- Customizable assistant responses based on user input.
- Streamlit web interface for user interaction.

## Installation

### Prerequisites

- Python 3.8+
- FastAPI
- SQLModel
- OpenAI
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

## API Reference

The project exposes the following API endpoints:

- /start: Initiates a new conversation with the AI assistant.
- /chat: Allows users to send messages and receive responses from the assistant.

## Contributing

Contributions are welcome! Follow these steps to contribute to the project:

1. Fork the repository.
2. Create a new branch (git checkout -b feature/improvement).
3. Make your changes and commit them (git commit -am 'Add new feature').
4. Push to the branch (git push origin feature/improvement).
5. Create a new Pull Request.

## Authors and Acknowledgment

This project was created by Harry.

## FAQs

**Q:** How can I customize the responses of the AI assistant?
**A:** You can modify the tools/functions defined in functions.py to tailor the assistant's behavior to your needs.

## Contact Information

For questions or suggestions, please contact harisjaved010@gmail.com.

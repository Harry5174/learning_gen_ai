import json
import os

def create_assistant(client):

    # Print the value of the client object
    print("Client object:", client)

    # Check if the client object is None
    if client is None:
        print("Error: Client object is None.")
        return None

    assets_folder = os.path.join(os.path.dirname(__file__), '..', 'assets')
    assistant_file_path = os.path.join(assets_folder, 'assistant.json')
    knowledge_file_path = os.path.join(assets_folder, '00_knowledge.docx')

    try:
        if os.path.exists(assistant_file_path):
            with open(assistant_file_path, 'r') as file:
                assistant_data = json.load(file)
                assistant_id = assistant_data.get('assistant_id')
                print("Loaded existing assistant ID.")
        else:
            with open(knowledge_file_path, "rb") as knowledge_file:
                file = client.files.create(file=knowledge_file, purpose='assistants')

            assistant = client.beta.assistants.create(
                instructions="""
                    Welcome to the AIOU University's Web Assistant! I'm here to assist you with any information related to the university's offerings and services. You can ask me questions about academic programs, admissions, campus facilities, events, and more.

                    Please note that I have been programmed to provide accurate information based on the resources available to me. If you have specific questions about university policies, procedures, or programs, feel free to ask, and I'll do my best to assist you.

                    Additionally, if you have a document containing information about the university's offerings and conditions, you can upload it here, and I can provide further assistance based on the content provided.

                    Let me know how I can help you today!    
                """,
                model="gpt-3.5-turbo-0125",
                tools=[{"type": "file_search"}]
            )

            with open(assistant_file_path, 'w') as file:
                json.dump({'assistant_id': assistant.id}, file)
                print("Created a new assistant and saved the ID.")

            assistant_id = assistant.id

        return assistant_id
    except Exception as e:
        print(f"Error occurred while creating or loading assistant: {e}")
        return None

import json
import os

def create_assistant(client):
    assistant_file_path = os.path.join(os.path.dirname(__file__), 'assistant.json')

    try:
        if os.path.exists(assistant_file_path):
            with open(assistant_file_path, 'r') as file:
                assistant_data = json.load(file)
                assistant_id = assistant_data.get('assistant_id')
                print("Loaded existing assistant ID.")
        else:
            with open("knowledge.docx", "rb") as knowledge_file:
                file = client.files.create(file=knowledge_file, purpose='assistants')

            assistant = client.beta.assistants.create(
                instructions="""
                The assistant, Harry's Customer Support Assistant, has been programmed to provide potential customers with information on the gym's offering.
                A document has been provided with information on Harry's offering and conditions.
                """,
                model="gpt-3.5-turbo-0125",
                tools=[{"type": "retrieval"}],
                file_ids=[file.id]
            )

            with open(assistant_file_path, 'w') as file:
                json.dump({'assistant_id': assistant.id}, file)
                print("Created a new assistant and saved the ID.")

            assistant_id = assistant.id

        return assistant_id
    except Exception as e:
        print(f"Error occurred while creating or loading assistant: {e}")
        return None

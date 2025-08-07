import json
import os

def create_assistant(client):
    assistant_file_path = 'assistant.json'

    if os.path.exists(assistant_file_path):
        with open(assistant_file_path, 'r') as file:
            assistant_data = json.load(file)
            assistant_id = assistant_data['assistant_id']
            print("Loaded existing assistant ID.")
    else:
        # Define the tools for the assistant with corrected naming and functionality
        instructions = "You are a personal math and programming tutor. Write and run code to answer math questions plus provide answers related to programming by sharing proper code and programs."
        # Create the assistant with the defined tools/functions
        assistant = client.beta.assistants.create(instructions=instructions, model="gpt-3.5-turbo-0125",
              tools=[{'type' : 'code_interpreter'}])

        # Save the assistant ID for future use
        with open(assistant_file_path, 'w') as file:
            json.dump({'assistant_id': assistant.id}, file)
            print("Created a new assistant and saved the ID.")

        assistant_id = assistant.id

    return assistant_id

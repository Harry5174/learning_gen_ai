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
        # Define the tools/functions for the assistant with corrected naming and functionality
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "create_person",
                    "description": "Create a new person record with name and location",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "The name of the person"},
                            "location": {"type": "string", "description": "The location of the person"},
                        },
                        "required": ["name", "location"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_person_location",
                    "description": "Retrieve the location of a person by their name",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "The name of the person"},
                        },
                        "required": ["name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "read_all_persons",
                    "description": "Get data of all persons in the database",
                    "parameters": {}
                }
            }
        ]

        # Create the assistant with the defined tools/functions
        assistant = client.beta.assistants.create(instructions="""
              The assistant will be responsible for communicating with the database to share locations of friends
              """, model="gpt-3.5-turbo-0125",
              tools=tools)

        # Save the assistant ID for future use
        with open(assistant_file_path, 'w') as file:
            json.dump({'assistant_id': assistant.id}, file)
            print("Created a new assistant and saved the ID.")

        assistant_id = assistant.id

    return assistant_id

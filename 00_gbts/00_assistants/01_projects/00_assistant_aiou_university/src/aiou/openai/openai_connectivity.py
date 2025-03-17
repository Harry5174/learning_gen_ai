from packaging import version
import openai
from dotenv import load_dotenv


def version_check():
    # Check OpenAI version is correct
    required_version = version.parse("1.1.1")
    current_version = version.parse(openai.__version__)
    #check version compatibility
    if current_version < required_version:
        raise ValueError(f"Error: OpenAI version {openai.__version__} is less than the required version 1.1.1")
    else:
        print("OpenAI version is compatible.")

def create_client(OPENAI_API_KEY):
    return openai.OpenAI(api_key=OPENAI_API_KEY)
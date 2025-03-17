# from langchain.llms import BaseLLM
# from typing import

# import subprocess
# import time

# class OllamaMistralLLM(BaseLLM):
#     def _llm_type(self):
#         return "mistral"

#     def _generate(self, prompts, **kwargs) -> list:
#         """Generate responses for a list of prompts."""
#         responses = []
#         for prompt in prompts:
#             response = self.call_mistral_model(prompt)
#             responses.append(response)
#         return responses

#     def call_mistral_model(self, prompt: str) -> str:
#         """Call the Mistral model using subprocess."""
#         result = subprocess.run(
#             ["ollama", "run", "mistral", prompt],
#             capture_output=True,
#             text=True
#         )
#         if result.returncode != 0:
#             raise RuntimeError(f"Ollama command failed: {result.stderr}")
#         return result.stdout.strip()

#     def stream_complete(self, prompt: str, **kwargs) -> Generator[str, None, None]:
#         """Stream responses for a single prompt."""
#         # Start the process to call the Mistral model
#         process = subprocess.Popen(
#             ["ollama", "run", "mistral", prompt],
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#             text=True
#         )

#         # Read the output line by line
#         try:
#             while True:
#                 output = process.stdout.readline()
#                 if output == '' and process.poll() is not None:
#                     break
#                 if output:
#                     yield output.strip()
#         finally:
#             process.kill()  # Ensure the process is killed when done

# # Example usage
# from llama_index.llms.langchain import LangChainLLM

# mistral_llm = LangChainLLM(llm=OllamaMistralLLM())

# # Streaming response example
# response_gen = mistral_llm.stream_complete("Hi, this is")
# for delta in response_gen:
#     print(delta, end="")

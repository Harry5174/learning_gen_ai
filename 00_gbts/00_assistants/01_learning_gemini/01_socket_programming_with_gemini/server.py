import socket
import logging
import os
from google import genai

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load API key securely (replace with environment variable or config management)
API_KEY = os.getenv("GOOGLE_GENAI_API_KEY")
if not API_KEY:
    logging.error("API key is missing. Set GOOGLE_GENAI_API_KEY environment variable.")
    exit(1)

# Initialize Google Gemini API Client
try:
    cl = genai.Client(api_key=API_KEY)
except Exception as e:
    logging.error(f"Failed to initialize Gemini API client: {e}")
    exit(1)

# Server Configuration
HOST = "0.0.0.0"  # Listen on all interfaces
PORT = 9999
BUFFER_SIZE = 1024

def handle_client(client_socket, address):
    """Handles communication with a connected client."""
    try:
        logging.info(f"Connected by {address}")
        with client_socket:
            while True:
                data = client_socket.recv(BUFFER_SIZE)
                if not data:
                    logging.info(f"Client {address} disconnected.")
                    break

                message = data.decode().strip()
                logging.info(f"Received from {address}: {message}")

                # Generate AI response
                try:
                    response = cl.models.generate_content(
                        model="gemini-2.0-flash",
                        contents=message,
                    ).text
                except Exception as e:
                    logging.error(f"Error generating AI response: {e}")
                    response = "Error processing request."

                client_socket.sendall(response.encode())
                logging.info(f"Sent to {address}: {response}")

    except Exception as e:
        logging.error(f"Error handling client {address}: {e}")

def start_server():
    """Starts the TCP server."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        logging.info(f"Server listening on {HOST}:{PORT}")

        try:
            while True:
                client_socket, addr = server_socket.accept()
                handle_client(client_socket, addr)

        except KeyboardInterrupt:
            logging.info("Server shutting down...")
        except Exception as e:
            logging.error(f"Server error: {e}")

if __name__ == "__main__":
    start_server()

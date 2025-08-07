import socket
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Server Configuration
SERVER_HOST = "localhost"
SERVER_PORT = 9999
BUFFER_SIZE = 1024

def start_client():
    """Starts the TCP client and handles communication with the server."""
    try:
        # Create a TCP/IP socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            logging.info(f"Connecting to {SERVER_HOST}:{SERVER_PORT}...")
            client.connect((SERVER_HOST, SERVER_PORT))
            logging.info("Connected to the server. Type 'exit' to quit.")

            while True:
                message = input("Enter a message: ").strip()
                if message.lower() == "exit":
                    logging.info("Exiting client...")
                    break

                logging.info(f"Sending: {message}")
                client.sendall(message.encode())

                # Receive a response from the server
                data = client.recv(BUFFER_SIZE)
                if not data:
                    logging.warning("Server closed the connection.")
                    break

                logging.info(f"Received: {data.decode()}")

    except (ConnectionRefusedError, ConnectionResetError) as e:
        logging.error(f"Connection error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
    finally:
        logging.info("Client disconnected.")

if __name__ == "__main__":
    start_client()

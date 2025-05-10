import json
import logging
import requests
from pathlib import Path


class TrackingClient:
    """Client for handling tracking-related HTTP requests and file operations."""
    
    def __init__(self, domain: str = "localhost", port: int = 8080, file_path: str = "session_tracking.json"):
        """
        Initialize the tracking client.
        
        Args:
            domain (str): The domain for the tracking server
            port (int): The port for the tracking server
            file_path (str): The path where tracking data will be saved
        """
        self.domain = domain
        self.port = port
        self.file_path = file_path
        self.base_url = f"http://{domain}:{port}"

    def update_session_tracking(self, session_id: str) -> bool:
        """
        Updates the tracking information for a specific session.
        
        Args:
            session_id (str): The ID of the session to track
            
        Returns:
            bool: True if the update was successful, False otherwise
        """
        if not session_id:
            logging.warning("No session ID provided for tracking update")
            return False

        try:
            # Construct the URL
            url = f"{self.base_url}/iracing-session/{session_id}"
            
            # Make the GET request
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for bad status codes
            
            # Create the directory if it doesn't exist
            file_path = Path(self.file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write the response to file
            with open(file_path, 'w') as f:
                json.dump(response.json(), f, indent=2)
            
            logging.info(f"Successfully updated tracking information for session {session_id}")
            return True
            
        except requests.RequestException as e:
            logging.error(f"Failed to update tracking information: {e}")
            return False
        except (json.JSONDecodeError, IOError) as e:
            logging.error(f"Failed to save tracking information to file: {e}")
            return False 
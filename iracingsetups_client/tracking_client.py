import json
import logging
import os
import requests
from pathlib import Path
from iracingsetups_client.json_to_properties import flatten_json

class TrackingClient:
    """Client for handling tracking-related HTTP requests and file operations."""
    
    def __init__(self, user_id: str, domain: str = "localhost", port: int = 8080, base_dir: str = "."):
        """
        Initialize the tracking client.
        
        Args:
            user_id (str): The user ID for tracking
            domain (str): The domain for the tracking server
            port (int): The port for the tracking server
            base_dir (str): The base directory where tracking data will be saved
        """
        self.user_id = user_id
        self.domain = domain
        self.port = port
        self.base_url = f"http://{domain}:{port}"
        
        # Ensure base directory exists and is writable
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        if not os.access(self.base_dir, os.W_OK):
            raise PermissionError(f"Directory {base_dir} is not writable")
            
        self.session_tracking_file = self.base_dir / "session_tracking.json"

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
            url = f"{self.base_url}/iracing-session/current/{self.user_id}-{session_id}"
            
            # Make the GET request
            response = requests.get(url)
            
            # Handle different HTTP status codes
            if response.status_code == 404:
                logging.warning(f"Session {session_id} not found on server")
                return False
            elif response.status_code >= 500:
                logging.error(f"Server error while updating tracking information: {response.status_code}")
                return False
                
            response.raise_for_status()  # Raise an exception for other bad status codes
            
            # Write the response to file
            with open(self.session_tracking_file, 'w') as f:
                flatten_json(response.json(), "current_session")
            
            logging.info(f"Successfully updated tracking information for session {session_id}")
            return True
            
        except requests.RequestException as e:
            logging.error(f"Failed to update tracking information: {e}")
            return False
        except (json.JSONDecodeError, IOError) as e:
            logging.error(f"Failed to save tracking information to file: {e}")
            return False 
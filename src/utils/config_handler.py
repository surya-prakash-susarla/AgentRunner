import json
import os
import subprocess
from pathlib import Path

from src.utils.logging_config import setup_logger
import logging

logger = setup_logger(__name__, logging.INFO)

CONFIG_DIR = os.path.expanduser("~/.replica-llm")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

DEFAULT_CONFIG = {
    "agentRuntimes": [
        {
            "runner": "gemini",
            "isMain": True,
            "api_key": ""  # Will be filled by user
        }
    ],
    "runtime": {
        "maxGlobalChildren": 100,
        "defaultTimeoutSeconds": 60
    },
    "toolServers": {}
}

def ensure_config_exists():
    """Ensure config directory and file exist, create if they don't"""
    try:
        # Create config directory if it doesn't exist
        os.makedirs(CONFIG_DIR, exist_ok=True)
        
        # Create config file if it doesn't exist
        if not os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'w') as f:
                json.dump(DEFAULT_CONFIG, f, indent=2)
            logger.info(f"Created default config file at {CONFIG_FILE}")
    except Exception as e:
        logger.error(f"Error ensuring config exists: {str(e)}")
        raise

def edit_config():
    """Open the config file in the user's preferred editor"""
    try:
        ensure_config_exists()
        
        # Get the user's preferred editor, fall back to vim
        editor = os.environ.get('EDITOR', 'vim')
        
        # Open the config file in the editor
        logger.info(f"Opening config file with {editor}")
        subprocess.run([editor, CONFIG_FILE])
        
        # Verify the config is valid JSON after editing
        try:
            with open(CONFIG_FILE, 'r') as f:
                json.load(f)
            logger.info("Config file successfully updated")
        except json.JSONDecodeError:
            logger.error("Warning: Config file contains invalid JSON!")
            
    except Exception as e:
        logger.error(f"Error editing config: {str(e)}")
        raise

def get_config():
    """Read and return the current config"""
    try:
        ensure_config_exists()
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error reading config: {str(e)}")
        raise

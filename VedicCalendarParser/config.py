# Configuration settings for the Vedic Calendar Parser
import os

# Read DEBUG_MODE from .system_prompt if available
SYSTEM_PROMPT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.system_prompt')
DEBUG_MODE = True  # default
try:
    with open(SYSTEM_PROMPT_PATH, 'r') as f:
        for line in f:
            if 'DEBUG_MODE' in line:
                # Parse the value after '=' and strip whitespace/quotes
                value = line.split('=')[1].strip().replace("'", '').replace('"', '')
                DEBUG_MODE = value.upper() == 'TRUE'
except Exception as e:
    pass  # Fallback to default True if any error
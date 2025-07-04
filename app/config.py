import os
from dotenv import load_dotenv
import sys

# Construct the path to the .env file.
# It assumes the .env file is in the parent directory of this script's directory.
# This makes it robust, whether you run from the root or from inside the 'app' directory.
try:
    # The __file__ attribute is not always available (e.g., in some interactive environments)
    # so we wrap this in a try-except block.
    dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    if not os.path.exists(dotenv_path):
        # Fallback for different execution contexts
        dotenv_path = os.path.join(os.getcwd(), '.env')
except NameError:
    dotenv_path = os.path.join(os.getcwd(), '.env')


load_dotenv(dotenv_path=dotenv_path)

# Retrieve the API key from the environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# A critical check to ensure the application doesn't start without the key.
if not GEMINI_API_KEY:
    # Using sys.exit() is a bit abrupt, but for a config file it ensures
    # the server won't even attempt to start without proper configuration.
    sys.exit("Error: GEMINI_API_KEY not found. Please set it in your .env file.")
else:
    print("GEMINI_API_KEY loaded successfully.")
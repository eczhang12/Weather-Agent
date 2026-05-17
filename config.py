# `os` is a standard Python library for interacting with the operating system.
# Here we use it to read environment variables, which are configuration values
# stored outside the code. API keys are usually stored this way so they are not
# committed to GitHub or baked into the program.
import os


# Read configuration from environment variables.
#
# `os.getenv("NAME", "")` means:
# - Look for an environment variable named NAME.
# - If it exists, return its string value.
# - If it does not exist, return the default value `""` instead.
#
# `python-dotenv` loads variables from `.env` in `main.py` before this module is
# imported by the application. After that, `os.getenv()` can read them as if they
# were normal shell environment variables.

# OpenAI uses this key to authenticate requests to the language model.
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# OpenWeatherMap uses this key to authenticate live weather API requests.
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")

# This chooses which OpenAI model the weather agent should use.
# If `.env` does not define OPENAI_MODEL, the app falls back to "gpt-4.1-mini".
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

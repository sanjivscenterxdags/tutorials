#
# Oct 9, 2026
#
# skeleton main.py
#

import os

from dotenv import load_dotenv


def main() -> None:
    print("Hello from langchain-course!")
    print("Current working directory:", os.getcwd())
    load_dotenv()  # Load environment variables from .env file
    print("Environment variables loaded.")
    # print("OPENAI_API_KEY:", os.getenv("OPENAI_API_KEY"))
    # print("GOOGLE_API_KEY:", os.getenv("GOOGLE_API_KEY"))


if __name__ == "__main__":
    main()

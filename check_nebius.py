
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

project_root = Path(__file__).resolve().parent
load_dotenv(project_root / ".env")

api_key = os.getenv("NEBIUS_TOKEN_FACTORY_KEY")

if not api_key or api_key == "PASTE_YOUR_REAL_KEY_HERE":
    raise SystemExit(
        "API key missing. Check the project-root .env file."
    )

client = OpenAI(
    api_key=api_key,
    base_url="https://api.tokenfactory.nebius.com/v1/",
)

try:
    models = client.models.list()

    print("\nConnected to Nebius Token Factory.")
    print("\nAvailable Nemotron models:")

    found = False
    for model in models.data:
        if "nemotron" in model.id.lower():
            print("-", model.id)
            found = True

    if not found:
        print("No Nemotron models appeared in this account's list.")

except Exception as exc:
    print("\nCould not verify the model list.")
    print("Error type:", type(exc).__name__)
    print("Check your API key, network, and Token Factory access.")
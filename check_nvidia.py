
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

def main():
    print("JARVIS: Starting NVIDIA Nemotron connection test...", flush=True)

    project_root = Path(__file__).resolve().parent
    env_file = project_root / ".env"

    print(f"Project folder: {project_root}", flush=True)
    print(f".env file exists: {env_file.is_file()}", flush=True)

    load_dotenv(env_file, override=True)

    api_key = os.getenv("NVIDIA_API_KEY")
    base_url = os.getenv(
        "NVIDIA_BASE_URL",
        "https://integrate.api.nvidia.com/v1",
    )
    model = os.getenv(
        "NVIDIA_MODEL",
        "nvidia/nemotron-3.5-bolt-e4b",
    )

    if not api_key or api_key == "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":
        print("ERROR: NVIDIA_API_KEY is missing from .env.", flush=True)
        return 1

    print(f"Model selected: {model}", flush=True)
    print("Sending test request to NVIDIA...", flush=True)

    try:
        client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=60.0,
            max_retries=0,
        )

        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are JARVIS, a calm and helpful "
                        "personal AI assistant."
                    ),
                },
                {
                    "role": "user",
                    "content": "Introduce yourself in two sentences.",
                },
            ],
            max_tokens=150,
        )

        reply = response.choices[0].message.content
        print("\nSUCCESS: NVIDIA API responded!", flush=True)
        print("JARVIS:", reply, flush=True)
        return 0

    except Exception as exc:
        print("\nNVIDIA request failed.", flush=True)
        print("Error type:", type(exc).__name__, flush=True)
        print("Error details:", str(exc)[:800], flush=True)
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(
            f"Unexpected error: {type(exc).__name__}: {exc}",
            flush=True,
        )
        sys.exit(1)

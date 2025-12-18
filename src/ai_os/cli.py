# src/ai_os/cli.py

import click
import requests

API_URL = "http://127.0.0.1:8000"

@click.group()
def cli():
    pass

@cli.command()
def health():
    r = requests.get(f"{API_URL}/health")
    print(r.json())

@cli.command()
def models():
    r = requests.get(f"{API_URL}/v1/models")
    print(r.json())

@cli.command()
@click.argument("model")
@click.argument("prompt")
def infer(model, prompt):
    r = requests.post(
        f"{API_URL}/v1/infer",
        json={"model": model, "prompt": prompt},
        timeout=10,
    )

    if r.status_code != 200:
        print("Error:", r.status_code)
        print(r.text)
        return

    try:
        print(r.json())
    except Exception:
        print("Non-JSON response:")
        print(r.text)


if __name__ == "__main__":
    cli()

"""One function LLM dispatch: anthropic | gemini | openai (any OpenAI-compatible endpoint).

# ponytail: no streaming, no chat history, no retry/backoff beyond what callers already
# do (text_aligner.py's own validation retry loop) — upgrade path is a shared retry
# wrapper if a 4th provider or long-context chat is ever needed.
"""
import json
import os
import subprocess
import time

import requests

from utils.env import load_env

load_env()

DEFAULT_ANTHROPIC_MODEL = "claude-sonnet-5"
# ponytail: gemini-2.0-flash was retired by Google; gemini-3.6-flash confirmed live
# via a direct curl against generateContent on 2026-09-10 — bump again if it 404s.
DEFAULT_GEMINI_MODEL = "gemini-3.6-flash"
DEFAULT_OPENAI_BASE_URL = "http://localhost:11434/v1"
DEFAULT_OPENAI_MODEL = "llama3.2"


def _sleep_seconds(provider):
    env_val = os.environ.get("LLM_SLEEP_SECONDS")
    if env_val:
        return float(env_val)
    return 6.0 if provider == "gemini" else 0.0


def _complete_anthropic(prompt, system):
    import anthropic

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    model = os.environ.get("LLM_MODEL") or DEFAULT_ANTHROPIC_MODEL
    kwargs = {
        "model": model,
        "max_tokens": 4096,
        "messages": [{"role": "user", "content": prompt}],
    }
    if system:
        kwargs["system"] = system
    response = client.messages.create(**kwargs)
    return "".join(block.text for block in response.content if block.type == "text")


def _complete_gemini(prompt, system):
    api_key = os.environ["GOOGLE_API_KEY"]
    model = os.environ.get("LLM_MODEL") or DEFAULT_GEMINI_MODEL
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        f"?key={api_key}"
    )
    body = {"contents": [{"role": "user", "parts": [{"text": prompt}]}]}
    if system:
        body["systemInstruction"] = {"parts": [{"text": system}]}
    resp = requests.post(url, json=body, timeout=120)
    resp.raise_for_status()
    data = resp.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]


def _complete_openai(prompt, system):
    base_url = os.environ.get("LLM_BASE_URL") or DEFAULT_OPENAI_BASE_URL
    model = os.environ.get("LLM_MODEL") or DEFAULT_OPENAI_MODEL
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    headers = {"Content-Type": "application/json"}
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    resp = requests.post(
        f"{base_url.rstrip('/')}/chat/completions",
        json={"model": model, "messages": messages},
        headers=headers,
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def _complete_claude_cli(prompt, system):
    # ponytail: shells out to the locally-logged-in `claude` CLI instead of the
    # Anthropic SDK — for machines with no standalone ANTHROPIC_API_KEY but an
    # authenticated Claude Code session. cwd=/tmp so no project hooks/CLAUDE.md fire.
    # No `system` support (CLI has no --system flag for -p mode) — folded into prompt.
    full_prompt = f"{system}\n\n{prompt}" if system else prompt
    model = os.environ.get("LLM_MODEL") or "sonnet"
    # Our own .env sets ANTHROPIC_API_KEY (often an invalid/OAuth token, see
    # DEFAULT_ANTHROPIC_MODEL comment above) -- strip it so the CLI uses its own
    # logged-in session instead of trying that key and stalling/erroring.
    env = os.environ.copy()
    env.pop("ANTHROPIC_API_KEY", None)
    result = subprocess.run(
        # --setting-sources "" skips user/project settings (plugins, hooks, MCP servers):
        # measured 112 s -> 4.6 s per call on this machine. --strict-mcp-config = no MCP.
        ["claude", "-p", "--output-format", "json", "--model", model,
         "--setting-sources", "", "--strict-mcp-config", full_prompt],
        capture_output=True,
        text=True,
        timeout=180,
        cwd="/tmp",
        env=env,
    )
    if result.returncode != 0:
        raise RuntimeError(f"claude -p failed (exit {result.returncode}): {result.stderr}")
    envelope = json.loads(result.stdout)
    return envelope["result"]


_PROVIDERS = {
    "anthropic": _complete_anthropic,
    "gemini": _complete_gemini,
    "openai": _complete_openai,
    "claude-cli": _complete_claude_cli,
}


def complete(prompt: str, system: str | None = None) -> str:
    """Dispatch a single-turn completion to the provider set by LLM_PROVIDER."""
    provider = os.environ.get("LLM_PROVIDER", "anthropic").lower()
    if provider not in _PROVIDERS:
        raise ValueError(f"Unknown LLM_PROVIDER '{provider}'; expected one of {list(_PROVIDERS)}")

    text = _PROVIDERS[provider](prompt, system)

    sleep_for = _sleep_seconds(provider)
    if sleep_for:
        time.sleep(sleep_for)

    return text

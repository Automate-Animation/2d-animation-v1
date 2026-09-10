# ponytail: 10-line .env loader — swap for python-dotenv if the project ever needs
# nested/quoted values or multiple env files; stdlib is enough for flat KEY=VALUE today.
import os


def load_env(path=None):
    path = path or os.path.join(os.path.dirname(__file__), "..", "..", ".env")
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key, value = key.strip(), value.strip().strip('"').strip("'")
            os.environ.setdefault(key, value)

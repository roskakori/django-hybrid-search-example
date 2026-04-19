#!/usr/bin/env python3
import logging
import subprocess
from pathlib import Path

_DOT_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
_VENV_PATH = Path(__file__).resolve().parent.parent / ".venv"

_log = logging.getLogger("set_up_project")


def _run_command(description: str, command_parts: list[str]):
    cleaned_parts = [part if " " not in part else f'"{part}"' for part in command_parts]
    if description != "":
        _log.info(description)
    _log.info(f"{' '.join(cleaned_parts)}")
    subprocess.run(command_parts, check=True)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    _run_command(
        "🐙 Allowing commit messages to start with hash (#)",
        ["git", "config", "--local", "core.commentChar", ";"],
    )
    if not _VENV_PATH.exists():
        _run_command(
            "🐍 Creating or updating Python environment",
            ["uv", "venv", "--allow-existing"],
        )
    else:
        _log.info("ℹ️ Keeping existing Python environment")  # noqa: RUF001
    _run_command("📦 Installing packages", ["uv", "sync", "--all-groups"])
    _run_command("🪝 Setting up pre-commit hooks", ["uv", "run", "prek", "install"])
    if not _DOT_ENV_PATH.exists():
        _log.info("⚙️ Creating default .env file")
        demo_password = "Demo.123"
        _DOT_ENV_PATH.write_text(
            "\n".join(
                [
                    f"DHSE_DEMO_PASSWORD={demo_password}",
                    "DHSE_OLLAMA_URL=http://localhost:11438",
                    "DHSE_POSTGRES_DATABASE=dhse",
                    "DHSE_POSTGRES_HOST=localhost",
                    f"DHSE_POSTGRES_PASSWORD={demo_password}",
                    "DHSE_POSTGRES_PORT=5438",
                    "DHSE_POSTGRES_USERNAME=dhse",
                ]
            )
        )
    else:
        _log.info("ℹ️ Keeping existing environment file")  # noqa: RUF001
    _log.info("✅ The project was set up successfully.")
    _log.info("📖 Refer to the README.md on how to proceed.")

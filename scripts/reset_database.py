#!/usr/bin/env python3
import logging
import os
import subprocess

import dotenv

_log = logging.getLogger("reset_database")


def _run_manage_py(description: str, command_parts: list[str], *, env=None):
    actual_env = os.environ | (env or {})
    _run_command(description, ["uv", "run", "python", "manage.py", *command_parts], env=actual_env)


def _run_command(description: str, command_parts: list[str], *, env=None):
    cleaned_parts = [part if " " not in part else f'"{part}"' for part in command_parts]
    if description != "":
        _log.info(description)
    _log.info(f"{' '.join(cleaned_parts)}")
    subprocess.run(command_parts, check=True, env=env)


if __name__ == "__main__":
    dotenv.load_dotenv()
    demo_password = os.getenv("DHSE_DEMO_PASSWORD", "Demo.123")
    logging.basicConfig(level=logging.INFO)
    _run_command("💤  Shutting down database", ["docker", "compose", "down", "postgres"])
    _run_command(
        "💥 Removing database docker volume",
        ["docker", "volume", "remove", "--force", "django-hybrid-search-example_dhse_postgres_data"],
    )
    _run_command("🐳 Shutting down database", ["docker", "compose", "up", "--detach", "--wait", "postgres"])
    _run_manage_py("🚀 Applying migrations", ["migrate"])
    _run_manage_py(
        "🧙 Create admin user",
        ["createsuperuser", "--no-input", "--username", "admin", "--email", "admin@localhost"],
        env={"DJANGO_SUPERUSER_PASSWORD": demo_password},
    )
    _log.info("✅ The database was reset successfully.")
    _run_manage_py("🚓 Checking for possibly missing migrations", ["makemigrations", "--dry-run"])

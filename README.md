# django-hybrid-search-example

This repository contains the slides and example code for a talk given at PyCon Austria 2026 about doing multilingual hybrid search in Django.

## Local setup

Install the following:

- [Python 3.12](https://www.python.org/downloads/) or later
- [git](https://git-scm.com/) for version control
- [uv](https://docs.astral.sh/uv/) for Python package management
- [Docker](https://www.docker.com/) unless you want to use your own PostgreSQL database with the [pg_vector](https://github.com/pgvector/pgvector) extension installed.

Navigate to a folder where you want to store the project in, for example:

```bash
cd ~/Projects  # ...or which ever folder you prefer.
```

Clone the repository:

```bash
git clone https://github.com/roskakori/django-hybrid-search-example.git
```

Change into the project directory:

```bash
cd django-hybrid-search-example
```

Optionally, create a `.env` file. If you skip this, a default is created during the next step which should look similar to:

```dotenv
# Example settings
DHSE_DEMO_PASSWORD=Demo.123
DHSE_POSTGRES_DATABASE=dhse
DHSE_POSTGRES_HOST=localhost
DHSE_POSTGRES_PASSWORD=DEMO_PASSWORD
DHSE_POSTGRES_PORT=5438
DHSE_POSTGRES_USERNAME=dhse
```

Run the setup script:

```bash
python scripts/set_up_project.py
```

which essentially does the following:

1. Create a Python virtual environment.
2. Install pre-commit hooks to ensure basic code quality.
3. Create a `.env` environment file holding settings like the database connection.
4. Allow git commit messages to start with issues numbers like `#123`.

Review the `.env` file if you want to change anything. By default, everything should work out of the box and use the services specified in the `compose.yaml`.

Launch the database and ollama service:

```bash
docker compose up --detach
```

Apply the database migrations:

```bash
uv run python manage.py migrate
```

Create a superuser with a password of your choice, for example:

```bash
uv run python manage.py createsuperuser --username admin --email admin@example.com
```

Run the server on a port of your choice, for example:

```bash
uv run python manage.py runserver 8008
```

## Adding documents

To add a document, use "Add document" in the navigation bar or the admin site.

Alternatively, you can use the command line:

```bash
uv run python manage.py add_document en "fox & dog" "the quick brown fox jumped over the lazy white dog"
```

Use the `--file` option to interpret the CONTENT option as a file path, for example:

```bash
uv run python manage.py add_document --file  en "fox & dog" fox_and_dog.txt
```

This will read the `Document.content` from "fox_and_dog.txt".

## Computing search vectors

After adding a document, the full-text search vectors are automatically computed.

The computation of the semantic search vectors has to be initiated manually:

```bash
uv run python manage.py update_all_document_sematic_vectors
```

This will update all documents that have no semantic search vector yet.

To recompute the search vectors for all documents, including the ones that already have one, run:

```bash
uv run python manage.py update_all_document_sematic_vectors --force
```

## Removing all documents

To remove all documents from the database:

```bash
uv run python manage.py remove_all_documents
```

To remove only German documents:

```bash
uv run python manage.py remove_all_documents de
```

## Resetting the database

During experimenting, it can be useful to restart with a clean database and data model.

To clear all the data in the database but preserve the data model and reload the migration data:

```bash
uv run python scripts/reset_database.py
```

To go a step further and even rebuild the database migrations from scratch:

```bash
rm -f core/migrations/0???_*.py && \
uv run python scripts/reset_database.py && \
uv run python manage.py makemigrations && \
uv run python manage.py migrate
```

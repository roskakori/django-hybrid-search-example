from django.core.management.base import BaseCommand

from core.ollama_session import OllamaSession
from core.writers import update_all_document_semantic_vectors


class Command(BaseCommand):
    help = "Add a new document"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Update all documents including the ones that already have a semantic vector",
        )

    def handle(self, *args, **options):
        force = options["force"]
        with OllamaSession() as ollama_session:
            documents_to_update_count, document_count = update_all_document_semantic_vectors(
                ollama_session, force=force
            )

        self.stdout.write(
            self.style.SUCCESS(f"Updated semantic vectors of {documents_to_update_count}/{document_count} documents")
        )

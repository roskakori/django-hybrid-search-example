from django.core.management.base import BaseCommand

from core.models import Document, IsoLanguage


class Command(BaseCommand):
    help = "Remove all documents"

    def add_arguments(self, parser):
        parser.add_argument(
            "iso_language",
            type=IsoLanguage,
            nargs="?",
            metavar="LANGUAGE",
            help=(
                "ISO 639-1 language code matching any of the supported languages; "
                "use 'xx' for other languages; "
                "default: all languages"
            ),
        )

    def handle(self, *args, **options):
        iso_language = options["iso_language"]
        documents_to_remove = Document.objects.all()
        if iso_language is not None:
            documents_to_remove = documents_to_remove.filter(iso_language=iso_language)
        removed_documents_count = documents_to_remove.count()
        documents_count = Document.objects.count()
        documents_to_remove.delete()

        self.stdout.write(
            self.style.SUCCESS(f"Successfully removed {removed_documents_count}/{documents_count} documents.")
        )

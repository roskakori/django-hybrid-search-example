from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from core.models import Document, IsoLanguage


class Command(BaseCommand):
    help = "Add a new document"

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            action="store_true",
            help="Interpret content as a file path and read the document content from it",
        )
        parser.add_argument(
            "iso_language",
            type=IsoLanguage,
            metavar="LANGUAGE",
            help="ISO 639-1 language code matching any of the supported languages; use 'xx' for other languages",
        )
        parser.add_argument(
            "title",
            metavar="TITLE",
            type=str,
            help="The title of the document",
        )
        parser.add_argument(
            "content",
            metavar="CONTENT_OR_PATH",
            type=str,
            nargs="?",
            default="",
            help="Optional document content or file path when --file is set",
        )

    def handle(self, *args, **options):
        iso_language = options["iso_language"]
        title = options["title"]
        content = options["content"]
        use_file = options["file"]

        if use_file:
            file_path = Path(content)
            try:
                content = file_path.read_text(encoding="utf-8")
            except OSError as error:
                raise CommandError(f"Cannot read content file '{file_path}': {error}") from error

        document = Document.objects.create(
            iso_language=iso_language,
            title=title,
            content=content,
        )

        self.stdout.write(self.style.SUCCESS(f"Created document with id={document.pk}"))

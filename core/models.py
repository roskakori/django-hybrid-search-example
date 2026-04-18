from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVector, SearchVectorField
from django.db import models
from django.db.models import Case, TextChoices, When

MAX_TITLE_LENGTH = 200


class IsoLanguage(TextChoices):
    """
    ISO 639-1 language codes and their human-readable names.
    """

    ENGLISH = "en", "English"
    FRENCH = "fr", "French"
    GERMAN = "de", "German"
    ITALIAN = "it", "Italian"
    OTHER = "xx", "Other"


"""
Mapping for IsoLanguage to the corresponding PostgreSQL ts_config name.

For a full list of available ts_config names, run the following SQL query:

```sql
select cfgname from pg_ts_config order by 1;
```
"""
ISO_LANGUAGE_TO_TS_CONFIG_MAP = {
    IsoLanguage.ENGLISH: "english",
    IsoLanguage.FRENCH: "french",
    IsoLanguage.GERMAN: "german",
    IsoLanguage.ITALIAN: "italian",
    IsoLanguage.OTHER: "simple",
}

"""
Mapping for IsoLanguage to the corresponding Ollama embedding model name.

The standard models are available from <https://ollama.com/search?q=embedding>.
"""
_GWEN3_EMBEDDING_MODEL = "qwen3-embedding:0.6b"  # See <https://ollama.com/library/qwen3-embedding>.
_JINJA_BASE_DE_EMBEDDING_MODEL = "jina/jina-embeddings-v2-base-de"
_NOMIC_EMBEDDING_MODEL = "nomic-embed-text-v2-moe"

ISO_LANGUAGE_TO_EMBEDDING_MODEL_MAP = {
    IsoLanguage.ENGLISH: _GWEN3_EMBEDDING_MODEL,
    IsoLanguage.FRENCH: _GWEN3_EMBEDDING_MODEL,
    IsoLanguage.GERMAN: _JINJA_BASE_DE_EMBEDDING_MODEL,
    IsoLanguage.ITALIAN: _GWEN3_EMBEDDING_MODEL,
    IsoLanguage.OTHER: _GWEN3_EMBEDDING_MODEL,
}


class Document(models.Model):
    iso_language: IsoLanguage = models.CharField(
        choices=IsoLanguage.choices, default=IsoLanguage.OTHER, max_length=2, verbose_name="ISO language"
    )
    title: str = models.CharField(blank=True, default="", max_length=MAX_TITLE_LENGTH)
    content: str = models.TextField(blank=True, default="")
    fts_vector = models.GeneratedField(
        expression=Case(
            *[
                When(
                    iso_language=iso_language,
                    then=(
                        SearchVector("title", weight="A", config=config)
                        + SearchVector("content", weight="B", config=config)
                    ),
                )
                for iso_language, config in ISO_LANGUAGE_TO_TS_CONFIG_MAP.items()
            ],
            default=(
                SearchVector("title", weight="A", config="simple")
                + SearchVector("content", weight="B", config="simple")
            ),
        ),
        output_field=SearchVectorField(),
        db_persist=True,
        verbose_name="vector for full-text search",
    )

    class Meta:
        indexes = [GinIndex(fields=["fts_vector"], name="%(app_label)s_%(class)s_fts_vector_idx")]

    def __str__(self):
        return self.title


#
# The models below are only for demonstration purposes and
# are referenced on the slides but not used in the code.
#


class DocumentWithSingleFtsField(models.Model):
    iso_language: IsoLanguage = models.CharField(default=IsoLanguage.OTHER, max_length=2, choices=IsoLanguage.choices)
    title: str = models.CharField(blank=True, default="", max_length=MAX_TITLE_LENGTH)
    content: str = models.TextField(blank=True, default="")
    fts_vector = models.GeneratedField(
        expression=Case(
            *[
                When(iso_language=iso_language, then=SearchVector("title", weight="A", config=config))
                for iso_language, config in ISO_LANGUAGE_TO_TS_CONFIG_MAP.items()
            ],
            default=SearchVector("title", weight="A", config="simple"),
        ),
        output_field=SearchVectorField(),
        db_persist=True,
        verbose_name="vector for full-text search",
    )

    def __str__(self):
        return self.title


class DocumentFtsWithoutLoop(models.Model):
    iso_language: IsoLanguage = models.CharField(default=IsoLanguage.OTHER, max_length=2, choices=IsoLanguage.choices)
    title: str = models.CharField(blank=True, default="", max_length=MAX_TITLE_LENGTH)
    fts_vector = models.GeneratedField(
        expression=Case(
            When(iso_language=IsoLanguage.ENGLISH, then=SearchVector("title", weight="A", config="english")),
            When(iso_language=IsoLanguage.FRENCH, then=SearchVector("title", weight="A", config="french")),
            When(iso_language=IsoLanguage.GERMAN, then=SearchVector("title", weight="A", config="german")),
            When(iso_language=IsoLanguage.ITALIAN, then=SearchVector("title", weight="A", config="italian")),
            default=SearchVector("title", weight="A", config="simple"),
        ),
        output_field=SearchVectorField(),
        db_persist=True,
        verbose_name="vector for full-text search",
    )

    def __str__(self):
        return self.title


class DocumentFtsSingleLanguage(models.Model):
    title: str = models.CharField(blank=True, default="", max_length=MAX_TITLE_LENGTH)
    fts_vector = SearchVectorField(default=None, editable=False, null=True, verbose_name="vector for full-text search")

    def __str__(self):
        return self.title

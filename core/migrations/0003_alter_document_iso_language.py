from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0002_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="document",
            name="iso_language",
            field=models.CharField(
                choices=[
                    ("en", "English"),
                    ("fr", "French"),
                    ("de", "German"),
                    ("it", "Italian"),
                    ("xx", "Other"),
                ],
                default="en",
                max_length=2,
                verbose_name="ISO language",
            ),
        ),
    ]

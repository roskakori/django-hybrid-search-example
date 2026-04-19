# Copyright (C) 2023-2026 by Siisurit e.U., Austria. All rights reserved.
from django.db import migrations
from pgvector.django import VectorExtension


class Migration(migrations.Migration):
    operations = [VectorExtension()]

# Generated by Django 4.2.12 on 2024-10-02 12:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("boards", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="topic",
            name="views",
            field=models.PositiveIntegerField(default=0),
        ),
    ]
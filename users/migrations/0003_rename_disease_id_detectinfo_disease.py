# Generated by Django 4.2.7 on 2023-12-29 14:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_skindisease_detectinfo'),
    ]

    operations = [
        migrations.RenameField(
            model_name='detectinfo',
            old_name='disease_id',
            new_name='disease',
        ),
    ]

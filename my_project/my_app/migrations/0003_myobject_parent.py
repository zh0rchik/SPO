# Generated by Django 4.2.1 on 2024-05-25 12:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_app', '0002_myobject_data_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='myobject',
            name='parent',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]

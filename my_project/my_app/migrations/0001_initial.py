# Generated by Django 5.0.6 on 2024-05-20 11:10

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MyObject',
            fields=[
                ('id', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('value', models.CharField(blank=True, max_length=255, null=True)),
                ('source', models.CharField(blank=True, max_length=255, null=True)),
                ('target', models.CharField(blank=True, max_length=255, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('type', models.CharField(max_length=50)),
                ('uploaded_file', models.FileField(upload_to='uploads/')),
            ],
        ),
    ]
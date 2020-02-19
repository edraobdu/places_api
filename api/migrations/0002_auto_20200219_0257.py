# Generated by Django 3.0.3 on 2020-02-19 02:57

import api.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.DeleteModel(
            name='TestModel',
        ),
        migrations.AlterField(
            model_name='city',
            name='flag',
            field=models.ImageField(null=True, upload_to=api.models.flag_path),
        ),
        migrations.AlterField(
            model_name='country',
            name='flag',
            field=models.ImageField(null=True, upload_to=api.models.flag_path),
        ),
        migrations.AlterField(
            model_name='region',
            name='flag',
            field=models.ImageField(null=True, upload_to=api.models.flag_path),
        ),
    ]
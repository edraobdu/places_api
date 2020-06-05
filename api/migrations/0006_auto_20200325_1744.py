# Generated by Django 3.0.3 on 2020-03-25 17:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_added_local_code_to_region'),
    ]

    operations = [
        migrations.AlterField(
            model_name='citytranslation',
            name='language_code',
            field=models.CharField(choices=[('en', 'English'), ('es', 'Spanish')], max_length=2),
        ),
        migrations.AlterField(
            model_name='countrytranslation',
            name='language_code',
            field=models.CharField(choices=[('en', 'English'), ('es', 'Spanish')], max_length=2),
        ),
        migrations.AlterField(
            model_name='regiontranslation',
            name='language_code',
            field=models.CharField(choices=[('en', 'English'), ('es', 'Spanish')], max_length=2),
        ),
    ]
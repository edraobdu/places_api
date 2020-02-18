# Generated by Django 3.0.3 on 2020-02-18 17:17

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_auto_20200218_0524'),
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
            model_name='language',
            name='iso_code',
            field=models.CharField(choices=[('en', 'English'), ('es', 'Spanish')], max_length=2, unique=True),
        ),
        migrations.AlterField(
            model_name='languagetranslation',
            name='language_code',
            field=models.CharField(choices=[('en', 'English'), ('es', 'Spanish')], max_length=2),
        ),
        migrations.AlterField(
            model_name='regiontranslation',
            name='language_code',
            field=models.CharField(choices=[('en', 'English'), ('es', 'Spanish')], max_length=2),
        ),
        migrations.CreateModel(
            name='ZipCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('zip_code', models.CharField(max_length=6, validators=[django.core.validators.RegexValidator('^\\d{1,10}$')])),
                ('city', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cities', to='api.City')),
            ],
        ),
    ]

# Generated by Django 2.2.5 on 2019-10-26 03:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('corpora', '0005_auto_20191025_0932'),
    ]

    operations = [
        migrations.AddField(
            model_name='text',
            name='label',
            field=models.SlugField(default=''),
            preserve_default=False,
        ),
    ]
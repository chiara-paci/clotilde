# Generated by Django 2.1.4 on 2019-10-12 14:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('languages', '0003_auto_20190216_0922'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='language',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='nonword',
            options={'ordering': ['name']},
        ),
    ]

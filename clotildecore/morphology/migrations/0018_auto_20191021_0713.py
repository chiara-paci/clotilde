# Generated by Django 2.2.5 on 2019-10-21 07:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('morphology', '0017_auto_20191012_1454'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='root',
            options={'ordering': ['root']},
        ),
        migrations.AlterModelOptions(
            name='temaentry',
            options={'ordering': ['argument', 'value']},
        ),
    ]

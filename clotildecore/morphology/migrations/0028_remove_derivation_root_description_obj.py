# Generated by Django 2.1.4 on 2019-11-02 06:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('morphology', '0027_auto_20191101_1115'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='derivation',
            name='root_description_obj',
        ),
    ]
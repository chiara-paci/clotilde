# Generated by Django 2.1.4 on 2019-11-01 11:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('morphology', '0026_remove_temaentry_tema'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='temaentry',
            unique_together={('argument', 'value')},
        ),
    ]

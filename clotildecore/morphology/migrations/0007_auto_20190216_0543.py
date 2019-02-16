# Generated by Django 2.1.4 on 2019-02-16 05:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('morphology', '0006_word_cache_part_of_speech'),
    ]

    operations = [
        migrations.RenameField(
            model_name='derivation',
            old_name='description',
            new_name='description_obj',
        ),
        migrations.RenameField(
            model_name='derivation',
            old_name='root_description',
            new_name='root_description_obj',
        ),
        migrations.RenameField(
            model_name='derivation',
            old_name='tema',
            new_name='tema_obj',
        ),
        migrations.RenameField(
            model_name='fusionrule',
            old_name='description',
            new_name='description_obj',
        ),
        migrations.RenameField(
            model_name='fusionrule',
            old_name='tema',
            new_name='tema_obj',
        ),
        migrations.RenameField(
            model_name='inflection',
            old_name='description',
            new_name='description_obj',
        ),
        migrations.RenameField(
            model_name='root',
            old_name='description',
            new_name='description_obj',
        ),
        migrations.RenameField(
            model_name='root',
            old_name='tema',
            new_name='tema_obj',
        ),
    ]

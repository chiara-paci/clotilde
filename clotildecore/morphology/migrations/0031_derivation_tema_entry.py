# Generated by Django 2.1.4 on 2019-11-02 07:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('morphology', '0030_remove_root_description_obj'),
    ]

    operations = [
        migrations.AddField(
            model_name='derivation',
            name='tema_entry',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='morphology.TemaEntry'),
        ),
    ]
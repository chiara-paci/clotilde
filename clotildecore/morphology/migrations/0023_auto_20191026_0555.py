# Generated by Django 2.1.4 on 2019-10-26 05:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('morphology', '0022_auto_20191026_0554'),
    ]

    operations = [
        migrations.AlterField(
            model_name='regexpreverse',
            name='target',
            field=models.OneToOneField(on_delete='cascade', related_name='reverse', to='morphology.RegexpReplacement'),
        ),
    ]

# Generated by Django 2.2.5 on 2019-10-21 07:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0012_auto_20191012_1454'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='value',
            options={'ordering': ['string']},
        ),
        migrations.AlterField(
            model_name='value',
            name='string',
            field=models.CharField(db_index=True, max_length=1024, unique=True),
        ),
    ]
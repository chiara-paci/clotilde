# Generated by Django 2.1.4 on 2019-10-26 05:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0015_auto_20191022_0820'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entry',
            name='attribute',
            field=models.ForeignKey(on_delete='protect', to='base.Attribute'),
        ),
        migrations.AlterField(
            model_name='entry',
            name='value',
            field=models.ForeignKey(on_delete='protect', to='base.Value'),
        ),
        migrations.AlterField(
            model_name='subdescription',
            name='attribute',
            field=models.ForeignKey(on_delete='protect', to='base.Attribute'),
        ),
        migrations.AlterField(
            model_name='subdescription',
            name='value',
            field=models.ForeignKey(on_delete='protect', to='base.Description'),
        ),
    ]
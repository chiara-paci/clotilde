# Generated by Django 2.1.4 on 2019-11-03 08:16

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=1024, unique=True)),
                ('alphabetic_order', models.ForeignKey(on_delete='protect', related_name='d_set', to='base.AlphabeticOrder')),
                ('case_set', models.ForeignKey(default=1, on_delete='protect', related_name='b_set', to='base.CaseSet')),
                ('period_sep', models.ForeignKey(on_delete='protect', related_name='c_set', to='base.TokenRegexp')),
                ('token_regexp_set', models.ForeignKey(on_delete='protect', related_name='a_set', to='base.TokenRegexpSet')),
            ],
            options={
                'abstract': False,
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='NonWord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=1024, unique=True)),
                ('word', models.CharField(db_index=True, max_length=1024)),
                ('language', models.ForeignKey(on_delete='cascade', to='languages.Language')),
            ],
            options={
                'abstract': False,
                'ordering': ['name'],
            },
        ),
    ]

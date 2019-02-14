# Generated by Django 2.1.4 on 2019-02-14 15:57

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('base', '0004_auto_20190214_1518'),
    ]

    operations = [
        migrations.CreateModel(
            name='Derivation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=1024)),
                ('description', models.ForeignKey(on_delete='cascade', to='base.Description')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FusedWord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('word', models.CharField(db_index=True, editable=False, max_length=1024)),
            ],
        ),
        migrations.CreateModel(
            name='Fusion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=1024)),
                ('language', models.ForeignKey(on_delete='cascade', to='base.Language')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FusionRule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=1024)),
                ('description', models.ForeignKey(on_delete='cascade', to='base.Description')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FusionRuleRelation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.IntegerField()),
                ('fusion', models.ForeignKey(on_delete='cascade', to='morphology.Fusion')),
                ('fusion_rule', models.ForeignKey(on_delete='cascade', to='morphology.FusionRule')),
            ],
        ),
        migrations.CreateModel(
            name='FusionWordRelation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.IntegerField()),
                ('fused_word', models.ForeignKey(on_delete='cascade', to='morphology.FusedWord')),
            ],
        ),
        migrations.CreateModel(
            name='Inflection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dict_entry', models.BooleanField(default=False)),
                ('description', models.ForeignKey(on_delete='cascade', to='base.Description')),
            ],
        ),
        migrations.CreateModel(
            name='Paradigma',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=1024)),
                ('language', models.ForeignKey(on_delete='cascade', to='base.Language')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ParadigmaInflection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('inflection', models.ForeignKey(on_delete='cascade', to='morphology.Inflection')),
                ('paradigma', models.ForeignKey(on_delete='cascade', to='morphology.Paradigma')),
            ],
        ),
        migrations.CreateModel(
            name='PartOfSpeech',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=1024)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RegexpReplacement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pattern', models.CharField(max_length=1024)),
                ('replacement', models.CharField(max_length=1024)),
            ],
        ),
        migrations.CreateModel(
            name='Root',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('root', models.CharField(max_length=1024)),
                ('description', models.ForeignKey(on_delete='cascade', to='base.Description')),
                ('language', models.ForeignKey(on_delete='cascade', to='base.Language')),
                ('part_of_speech', models.ForeignKey(on_delete='cascade', to='morphology.PartOfSpeech')),
            ],
        ),
        migrations.CreateModel(
            name='Stem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('derivation', models.ForeignKey(on_delete='cascade', to='morphology.Derivation')),
                ('root', models.ForeignKey(on_delete='cascade', to='morphology.Root')),
            ],
        ),
        migrations.CreateModel(
            name='Tema',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=1024)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TemaArgument',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=1024)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TemaEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('argument', models.ForeignKey(on_delete='cascade', to='morphology.TemaArgument')),
                ('tema', models.ForeignKey(on_delete='cascade', to='morphology.Tema')),
            ],
        ),
        migrations.CreateModel(
            name='TemaValue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=1024)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Word',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('word', models.CharField(db_index=True, editable=False, max_length=1024)),
                ('inflection', models.ForeignKey(on_delete='cascade', to='morphology.Inflection')),
                ('stem', models.ForeignKey(on_delete='cascade', to='morphology.Stem')),
            ],
        ),
        migrations.AddField(
            model_name='temaentry',
            name='value',
            field=models.ForeignKey(on_delete='cascade', to='morphology.TemaValue'),
        ),
        migrations.AddField(
            model_name='root',
            name='tema',
            field=models.ForeignKey(on_delete='cascade', to='morphology.Tema'),
        ),
        migrations.AddField(
            model_name='paradigma',
            name='part_of_speech',
            field=models.ForeignKey(on_delete='cascade', to='morphology.PartOfSpeech'),
        ),
        migrations.AddField(
            model_name='inflection',
            name='regsub',
            field=models.ForeignKey(on_delete='cascade', to='morphology.RegexpReplacement'),
        ),
        migrations.AddField(
            model_name='fusionwordrelation',
            name='word',
            field=models.ForeignKey(on_delete='cascade', to='morphology.Word'),
        ),
        migrations.AddField(
            model_name='fusionrule',
            name='part_of_speech',
            field=models.ForeignKey(on_delete='cascade', to='morphology.PartOfSpeech'),
        ),
        migrations.AddField(
            model_name='fusionrule',
            name='regsub',
            field=models.ForeignKey(on_delete='cascade', to='morphology.RegexpReplacement'),
        ),
        migrations.AddField(
            model_name='fusionrule',
            name='tema',
            field=models.ForeignKey(on_delete='cascade', to='morphology.Tema'),
        ),
        migrations.AddField(
            model_name='fusedword',
            name='fusion',
            field=models.ForeignKey(on_delete='cascade', to='morphology.Fusion'),
        ),
        migrations.AddField(
            model_name='derivation',
            name='paradigma',
            field=models.ForeignKey(on_delete='cascade', to='morphology.Paradigma'),
        ),
        migrations.AddField(
            model_name='derivation',
            name='regsub',
            field=models.ForeignKey(on_delete='cascade', to='morphology.RegexpReplacement'),
        ),
        migrations.AddField(
            model_name='derivation',
            name='root_description',
            field=models.ForeignKey(on_delete='cascade', related_name='root_derivation_set', to='base.Description'),
        ),
        migrations.AddField(
            model_name='derivation',
            name='root_part_of_speech',
            field=models.ForeignKey(on_delete='cascade', to='morphology.PartOfSpeech'),
        ),
        migrations.AddField(
            model_name='derivation',
            name='tema',
            field=models.ForeignKey(on_delete='cascade', to='morphology.Tema'),
        ),
    ]

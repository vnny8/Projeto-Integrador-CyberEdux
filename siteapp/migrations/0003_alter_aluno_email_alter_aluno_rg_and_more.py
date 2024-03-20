# Generated by Django 5.0.1 on 2024-03-19 00:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('siteapp', '0002_disciplina_planoensino'),
    ]

    operations = [
        migrations.AlterField(
            model_name='aluno',
            name='email',
            field=models.CharField(max_length=100, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='aluno',
            name='rg',
            field=models.CharField(default='', max_length=50, unique=True),
        ),
        migrations.AlterField(
            model_name='professor',
            name='disciplina',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='siteapp.disciplina', unique='True'),
        ),
    ]

# Generated by Django 5.0.1 on 2024-03-19 13:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('siteapp', '0005_alter_professor_disciplina'),
    ]

    operations = [
        migrations.AddField(
            model_name='aluno',
            name='perfil',
            field=models.ImageField(default='fotos/padrao.png', upload_to='fotos/'),
        ),
        migrations.AddField(
            model_name='professor',
            name='perfil',
            field=models.ImageField(default='fotos/padrao.png', upload_to='fotos/'),
        ),
    ]
# Generated by Django 4.1.7 on 2023-03-20 21:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oauth_user', '0002_authuser_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='authuser',
            name='email',
            field=models.EmailField(max_length=150),
        ),
    ]

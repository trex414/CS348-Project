# Generated by Django 5.1 on 2024-10-16 21:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('part_1', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='foodentry',
            name='user_name',
            field=models.CharField(default='name', max_length=100),
            preserve_default=False,
        ),
    ]

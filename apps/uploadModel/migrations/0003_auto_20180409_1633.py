# Generated by Django 2.0.2 on 2018-04-09 15:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('uploadModel', '0002_testmodel_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='testmodel',
            name='checkpoint',
            field=models.FileField(default=None, upload_to='models'),
        ),
        migrations.AddField(
            model_name='testmodel',
            name='index_file',
            field=models.FileField(default=None, upload_to='models'),
        ),
    ]

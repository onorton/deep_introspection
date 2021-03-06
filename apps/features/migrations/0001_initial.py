# Generated by Django 2.0.2 on 2018-03-10 16:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('uploadModel', '0001_initial'),
        ('uploadImage', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FeatureSet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('features', models.FileField(upload_to='features')),
                ('image', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='uploadImage.TestImage')),
                ('model', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='uploadModel.TestModel')),
            ],
        ),
    ]

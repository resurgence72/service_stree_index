# Generated by Django 2.0 on 2022-02-25 04:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cloud_cmdb', '0004_auto_20220225_1104'),
    ]

    operations = [
        migrations.AddField(
            model_name='assetrecord',
            name='record_type',
            field=models.CharField(choices=[('c', 'create'), ('d', 'delete'), ('u', 'update')], default='c', max_length=1),
        ),
    ]

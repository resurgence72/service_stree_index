# Generated by Django 2.0 on 2022-02-24 11:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cloud_cmdb', '0002_auto_20220224_1950'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ecsinfo',
            name='instance_id',
            field=models.CharField(db_index=True, max_length=128, verbose_name='实例id'),
        ),
    ]

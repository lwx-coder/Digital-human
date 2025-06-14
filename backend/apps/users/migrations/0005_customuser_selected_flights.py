# Generated by Django 4.2.5 on 2025-05-10 09:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_update_default_roles'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='selected_flights',
            field=models.JSONField(blank=True, default=list, help_text='存储用户选择的航班ID列表', null=True, verbose_name='已选航班'),
        ),
    ]

# Generated by Django 4.0.6 on 2022-07-19 13:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('late_investigation', '0008_userdelay_alter_delay_users_userdelay_delay_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userdelay',
            name='is_checked',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='is_active',
            field=models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='number',
            field=models.PositiveSmallIntegerField(default=9999, verbose_name='number'),
        ),
        migrations.AlterField(
            model_name='delay',
            name='day',
            field=models.PositiveSmallIntegerField(default=19),
        ),
    ]

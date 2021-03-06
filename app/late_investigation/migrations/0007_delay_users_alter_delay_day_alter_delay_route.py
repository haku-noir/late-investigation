# Generated by Django 4.0.5 on 2022-07-17 04:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('late_investigation', '0006_remove_delay_date_delay_day_delay_month_delay_year'),
    ]

    operations = [
        migrations.AddField(
            model_name='delay',
            name='users',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='delay',
            name='day',
            field=models.PositiveSmallIntegerField(default=17),
        ),
        migrations.AlterField(
            model_name='delay',
            name='route',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='late_investigation.route'),
        ),
    ]

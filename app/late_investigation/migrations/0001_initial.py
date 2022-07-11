# Generated by Django 4.0.5 on 2022-07-11 05:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Model',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Sex',
            fields=[
                ('model_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='late_investigation.model')),
                ('name', models.CharField(max_length=50)),
            ],
            bases=('late_investigation.model',),
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('model_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='late_investigation.model')),
                ('name', models.CharField(max_length=20)),
                ('email', models.CharField(max_length=50)),
                ('sex_key', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='late_investigation.sex')),
            ],
            bases=('late_investigation.model',),
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('model_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='late_investigation.model')),
                ('user_key', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='late_investigation.user')),
            ],
            bases=('late_investigation.model',),
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('model_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='late_investigation.model')),
                ('number', models.PositiveSmallIntegerField()),
                ('user_key', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='late_investigation.user')),
            ],
            bases=('late_investigation.model',),
        ),
    ]

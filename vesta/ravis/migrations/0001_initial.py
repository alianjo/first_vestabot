# Generated by Django 3.0.8 on 2020-07-07 08:31

from django.db import migrations, models
import ravis.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Supplier',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=250)),
                ('address', models.CharField(max_length=250)),
                ('username', models.CharField(max_length=250)),
                ('password', models.CharField(max_length=250)),
                ('status', models.BooleanField(default=False)),
                ('credit', models.CharField(default='0.0', max_length=25)),
                ('name_rnd', models.CharField(default=ravis.models.random_string, max_length=250)),
                ('alias_name', models.CharField(default='', help_text='نام مستعار', max_length=250, verbose_name='alias name')),
            ],
        ),
    ]
# Generated by Django 5.0.12 on 2025-03-04 13:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoice', '0004_alter_invoiceerrors_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='fileupload',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='invoice.invoicednrdetails'),
        ),
    ]

# Generated by Django 5.2 on 2025-04-17 00:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0009_remove_venta_id_alter_venta_folio_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='venta',
            name='folio',
            field=models.CharField(editable=False, max_length=20, primary_key=True, serialize=False, unique=True),
        ),
    ]

# Generated by Django 5.1.3 on 2024-11-19 13:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('RRHH', '0002_rename_hr_extra_di_boleta_pago_biaticos_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='boleta_pago',
            old_name='biaticos',
            new_name='viaticos',
        ),
    ]
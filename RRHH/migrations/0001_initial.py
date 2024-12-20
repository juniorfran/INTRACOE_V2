# Generated by Django 5.1.3 on 2024-11-18 14:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Departamentos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_departamento', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Empleados',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50)),
                ('apellido', models.CharField(max_length=50)),
                ('dui', models.CharField(max_length=10)),
                ('codigo_empleado', models.CharField(max_length=10)),
                ('edad', models.IntegerField()),
                ('salario', models.IntegerField()),
                ('cargo', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=100)),
                ('num_telefono', models.CharField(max_length=10)),
            ],
            options={
                'verbose_name': 'Empleado',
                'verbose_name_plural': 'Empleados',
            },
        ),
        migrations.CreateModel(
            name='Cargo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_cargo', models.CharField(max_length=50)),
                ('departamento', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='RRHH.departamentos')),
            ],
        ),
        migrations.CreateModel(
            name='Boleta_pago',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_pago', models.DateField()),
                ('fecha_inicio', models.DateField()),
                ('fecha_fin', models.DateField()),
                ('dias_laborados', models.IntegerField()),
                ('descuento_afp', models.IntegerField()),
                ('descuento_isss', models.IntegerField()),
                ('descuento_renta', models.IntegerField()),
                ('otro_descuento1', models.IntegerField()),
                ('otro_descuento2', models.IntegerField()),
                ('total_descuentos', models.IntegerField()),
                ('hr_extra_di', models.IntegerField()),
                ('hr_extra_noc', models.IntegerField()),
                ('hr_extra_fer', models.IntegerField()),
                ('hr_extra_fer_noc', models.IntegerField()),
                ('total_pago', models.IntegerField()),
                ('liquido_recibir', models.IntegerField()),
                ('empleado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='RRHH.empleados')),
            ],
            options={
                'verbose_name': 'Boleta de pago',
                'verbose_name_plural': 'Boletas de pago',
            },
        ),
    ]

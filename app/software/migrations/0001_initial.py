# Generated by Django 3.2.20 on 2023-10-06 08:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Inspection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag', models.CharField(max_length=255)),
                ('sono', models.CharField(max_length=255)),
                ('ip', models.CharField(max_length=14)),
            ],
        ),
        migrations.CreateModel(
            name='Origin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='ProgramCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='TypicalActivity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='ProgramClass',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('program_category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='software.programcategory')),
            ],
        ),
        migrations.CreateModel(
            name='Directory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('origin', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='software.origin')),
                ('program_category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='software.programcategory')),
                ('program_class', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='software.programclass')),
                ('typical_activity', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='software.typicalactivity')),
            ],
        ),
        migrations.CreateModel(
            name='Data',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('version', models.CharField(max_length=255)),
                ('publisher', models.CharField(max_length=255)),
                ('comments', models.CharField(max_length=255)),
                ('arpregkey', models.CharField(max_length=255)),
                ('tmfirstappear', models.DateTimeField()),
                ('hostcount', models.IntegerField()),
                ('directory', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='software.directory')),
                ('inspection', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='software.inspection')),
            ],
        ),
    ]

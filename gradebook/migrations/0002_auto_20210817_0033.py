# Generated by Django 3.2.5 on 2021-08-16 21:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gradebook', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='gradebook',
            name='course',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='gradebook.course'),
        ),
        migrations.AddField(
            model_name='teacher',
            name='courses',
            field=models.ManyToManyField(through='gradebook.Gradebook', to='gradebook.Course'),
        ),
    ]
# Generated by Django 4.1.9 on 2023-09-17 16:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('operations', '0015_remove_rating_feedback_parent_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rating_feedback',
            name='product',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='operations.product'),
        ),
    ]

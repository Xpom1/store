# Generated by Django 4.1.9 on 2023-10-07 16:14

from django.db import migrations, models
import django.db.models.deletion
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
        ('operations', '0017_productpriceinfo'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='rating_feedback',
            name='Checking the existence of a parent',
        ),
        migrations.RemoveField(
            model_name='rating_feedback',
            name='commented',
        ),
        migrations.AddField(
            model_name='rating_feedback',
            name='level',
            field=models.PositiveIntegerField(default=0, editable=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='rating_feedback',
            name='lft',
            field=models.PositiveIntegerField(default=0, editable=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='rating_feedback',
            name='parent',
            field=mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='operations.rating_feedback'),
        ),
        migrations.AddField(
            model_name='rating_feedback',
            name='rght',
            field=models.PositiveIntegerField(default=0, editable=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='rating_feedback',
            name='tree_id',
            field=models.PositiveIntegerField(db_index=True, default=0, editable=False),
            preserve_default=False,
        ),
        migrations.AddConstraint(
            model_name='rating_feedback',
            constraint=models.UniqueConstraint(condition=models.Q(('parent', None)), fields=('user', 'product'), name='Checking the existence of a parent'),
        ),
    ]
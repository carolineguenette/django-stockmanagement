# Generated manually to keep the database schema aligned with catalogue models.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalogue", "0003_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="productpackaging",
            name="ratio",
            field=models.DecimalField(
                decimal_places=6,
                max_digits=18,
                verbose_name="Ratio",
            ),
        ),
        migrations.AlterField(
            model_name="productconfig",
            name="alert_threshold",
            field=models.DecimalField(
                decimal_places=6,
                max_digits=20,
                verbose_name="Low stock threshold",
            ),
        ),
    ]

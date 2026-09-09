# Generated manually to keep the database schema aligned with inventory models.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="stock",
            name="pack_quantity",
            field=models.DecimalField(
                decimal_places=6,
                max_digits=20,
                verbose_name="Pack Quantity",
            ),
        ),
        migrations.AlterField(
            model_name="movement",
            name="pack_quantity_init",
            field=models.DecimalField(decimal_places=6, max_digits=20, verbose_name="Initial Pack Quantity"),
        ),
        migrations.AlterField(
            model_name="movement",
            name="pack_quantity_final",
            field=models.DecimalField(decimal_places=6, max_digits=20, verbose_name="Final Pack Quantity"),
        ),
        migrations.AlterField(
            model_name="movement",
            name="pack_quantity_delta",
            field=models.DecimalField(decimal_places=6, max_digits=20, verbose_name="Delta Pack Quantity"),
        ),
        migrations.AlterField(
            model_name="movement",
            name="ref_quantity_init",
            field=models.DecimalField(decimal_places=6, max_digits=20, verbose_name="Initial Ref Quantity"),
        ),
        migrations.AlterField(
            model_name="movement",
            name="ref_quantity_final",
            field=models.DecimalField(decimal_places=6, max_digits=20, verbose_name="Final Ref Quantity"),
        ),
        migrations.AlterField(
            model_name="movement",
            name="ref_quantity_delta",
            field=models.DecimalField(decimal_places=6, max_digits=20, verbose_name="Delta Ref Quantity"),
        ),
        migrations.AlterField(
            model_name="transit",
            name="source_pack_quantity_send",
            field=models.DecimalField(
                decimal_places=6,
                max_digits=20,
                verbose_name="Source Pack Quantity Sent",
            ),
        ),
        migrations.AlterField(
            model_name="transit",
            name="dest_pack_quantity_received",
            field=models.DecimalField(
                blank=True,
                decimal_places=6,
                default=None,
                max_digits=20,
                null=True,
                verbose_name="Destination Pack Quantity Received",
            ),
        ),
    ]

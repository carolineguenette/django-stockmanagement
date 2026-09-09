# Generated manually to keep the database schema aligned with company.Uom.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("company", "0003_custom_company_countries"),
    ]

    operations = [
        migrations.AlterField(
            model_name="uom",
            name="ratio",
            field=models.DecimalField(
                decimal_places=12,
                max_digits=20,
                verbose_name="Ratio",
            ),
        ),
        migrations.AddConstraint(
            model_name="uom",
            constraint=models.CheckConstraint(
                condition=models.Q(("ratio__gt", 0)),
                name="company_uom_ratio_gt_zero",
                violation_error_message="The ratio must be greater than zero.",
            ),
        ),
    ]

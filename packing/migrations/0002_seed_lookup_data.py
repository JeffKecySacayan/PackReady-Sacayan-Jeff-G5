from django.db import migrations

TRIP_TYPES = ["Beach", "Business", "Camping", "City Tour"]
CATEGORIES = ["Clothes", "Toiletries", "Documents", "Electronics", "Medicines", "Other"]


def seed(apps, schema_editor):
    TripType = apps.get_model("packing", "TripType")
    Category = apps.get_model("packing", "Category")
    for name in TRIP_TYPES:
        TripType.objects.get_or_create(name=name)
    for name in CATEGORIES:
        Category.objects.get_or_create(name=name)


class Migration(migrations.Migration):
    dependencies = [("packing", "0001_initial")]
    operations = [migrations.RunPython(seed, migrations.RunPython.noop)]
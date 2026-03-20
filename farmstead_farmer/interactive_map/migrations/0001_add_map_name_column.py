from django.db import migrations


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.RunSQL(
            sql='ALTER TABLE interactive_map ADD COLUMN IF NOT EXISTS map_name VARCHAR(255);',
            reverse_sql='ALTER TABLE interactive_map DROP COLUMN IF EXISTS map_name;',
        ),
    ]

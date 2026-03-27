from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('interactive_map', '0002_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql='ALTER TABLE interactive_map ADD COLUMN IF NOT EXISTS is_private BOOLEAN NOT NULL DEFAULT FALSE;',
            reverse_sql='ALTER TABLE interactive_map DROP COLUMN IF EXISTS is_private;',
        ),
    ]

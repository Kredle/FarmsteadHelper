from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_customuser_has_map_customuser_is_map_private'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='subscription_expires_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]

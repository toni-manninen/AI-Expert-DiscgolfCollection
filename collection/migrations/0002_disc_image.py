from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('collection', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='disc',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='disc_images/'),
        ),
    ]

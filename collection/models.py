from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Collection(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='collection',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} collection"


class Disc(models.Model):
    collection = models.ForeignKey(
        Collection,
        on_delete=models.CASCADE,
        related_name='discs',
    )
    name = models.CharField(max_length=120)
    manufacturer = models.CharField(max_length=120)
    plastic = models.CharField(max_length=80)
    weight = models.DecimalField(max_digits=5, decimal_places=2)
    color = models.CharField(max_length=60)
    image = models.ImageField(upload_to='disc_images/', blank=True, null=True)
    acquired_at = models.DateTimeField()

    class Meta:
        ordering = ['-acquired_at', 'name']

    def __str__(self):
        return f"{self.name} ({self.manufacturer})"


class BagDisc(models.Model):
    collection = models.ForeignKey(
        Collection,
        on_delete=models.CASCADE,
        related_name='bag_discs',
    )
    disc = models.ForeignKey(
        Disc,
        on_delete=models.CASCADE,
        related_name='bag_entries',
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['collection', 'disc'],
                name='unique_disc_in_collection_bag',
            )
        ]
        ordering = ['-added_at']

    def clean(self):
        if self.disc_id and self.collection_id and self.disc.collection_id != self.collection_id:
            raise ValidationError('Disc must belong to the same collection.')

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.collection.user.username} bag: {self.disc.name}"

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from collection.models import BagDisc, Collection, Disc


DISC_TEMPLATES = [
    ("Destroyer", "Innova", "Star", "Yellow"),
    ("Wraith", "Innova", "Champion", "Orange"),
    ("Firebird", "Innova", "Champion", "Red"),
    ("Teebird", "Innova", "Star", "Blue"),
    ("Leopard3", "Innova", "GStar", "White"),
    ("Zone", "Discraft", "ESP", "Pink"),
    ("Buzzz", "Discraft", "Z Line", "Green"),
    ("Luna", "Discraft", "Jawbreaker", "Purple"),
    ("Hades", "Discraft", "ESP", "Teal"),
    ("Raptor", "Discraft", "Big Z", "Black"),
    ("Pure", "Latitude 64", "Opto", "Clear"),
    ("River", "Latitude 64", "Gold", "Sky Blue"),
    ("Saint", "Latitude 64", "Gold", "Lavender"),
    ("Explorer", "Latitude 64", "Opto", "Mint"),
    ("Felon", "Dynamic Discs", "Fuzion", "Gray"),
    ("Judge", "Dynamic Discs", "Classic", "Tan"),
    ("Truth", "Dynamic Discs", "Lucid", "Turquoise"),
    ("Aviar", "Innova", "DX", "White"),
    ("Envy", "Axiom", "Neutron", "Lime"),
    ("Hex", "Axiom", "Neutron", "Cyan"),
]


class Command(BaseCommand):
    help = "Create a test user with a 20-disc test collection."

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            type=str,
            default="test_user",
            help="Username for the test account.",
        )
        parser.add_argument(
            "--password",
            type=str,
            default="test12345",
            help="Password for the test account (used only when creating a new user).",
        )

    def handle(self, *args, **options):
        username = options["username"]
        password = options["password"]

        user_model = get_user_model()
        user, created = user_model.objects.get_or_create(
            username=username,
            defaults={"email": f"{username}@example.com"},
        )

        if created:
            user.set_password(password)
            user.save(update_fields=["password"])
            self.stdout.write(self.style.SUCCESS(f"Created user '{username}'."))
        else:
            self.stdout.write(f"Using existing user '{username}'.")

        collection, collection_created = Collection.objects.get_or_create(user=user)
        if collection_created:
            self.stdout.write(self.style.SUCCESS("Created collection."))
        else:
            self.stdout.write("Using existing collection.")

        # Keep this command idempotent by removing previous test entries for this collection.
        Disc.objects.filter(collection=collection).delete()

        now = timezone.now()
        created_discs = []

        for index, (name, manufacturer, plastic, color) in enumerate(DISC_TEMPLATES):
            disc = Disc.objects.create(
                collection=collection,
                name=name,
                manufacturer=manufacturer,
                plastic=plastic,
                weight=173.0 - (index % 6),
                color=color,
                acquired_at=now - timedelta(days=index * 4),
            )
            created_discs.append(disc)

        for disc in created_discs[:8]:
            BagDisc.objects.create(collection=collection, disc=disc)

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {len(created_discs)} discs for '{username}' and added 8 to the bag."
            )
        )

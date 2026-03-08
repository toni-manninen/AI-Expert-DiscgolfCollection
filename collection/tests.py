from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from .models import BagDisc, Collection, Disc


class ModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='alice', password='strong-pass-123')
        self.collection = Collection.objects.create(user=self.user)

    def test_collection_str(self):
        self.assertEqual(str(self.collection), 'alice collection')

    def test_disc_ordering_by_acquired_at_desc_then_name(self):
        now = timezone.now()
        newest = Disc.objects.create(
            collection=self.collection,
            name='Buzzz',
            manufacturer='Discraft',
            plastic='ESP',
            weight=Decimal('176.00'),
            color='Blue',
            acquired_at=now,
        )
        older = Disc.objects.create(
            collection=self.collection,
            name='Destroyer',
            manufacturer='Innova',
            plastic='Star',
            weight=Decimal('175.00'),
            color='White',
            acquired_at=now - timedelta(days=1),
        )

        discs = list(Disc.objects.filter(collection=self.collection))
        self.assertEqual(discs, [newest, older])

    def test_bag_disc_must_belong_to_same_collection(self):
        other_user = User.objects.create_user(username='bob', password='strong-pass-123')
        other_collection = Collection.objects.create(user=other_user)
        foreign_disc = Disc.objects.create(
            collection=other_collection,
            name='Hex',
            manufacturer='Axiom',
            plastic='Neutron',
            weight=Decimal('173.00'),
            color='Pink',
            acquired_at=timezone.now(),
        )

        with self.assertRaises(ValidationError):
            BagDisc.objects.create(collection=self.collection, disc=foreign_disc)

    def test_bag_disc_unique_constraint(self):
        disc = Disc.objects.create(
            collection=self.collection,
            name='Pure',
            manufacturer='Latitude 64',
            plastic='Zero Medium',
            weight=Decimal('174.00'),
            color='White',
            acquired_at=timezone.now(),
        )

        BagDisc.objects.create(collection=self.collection, disc=disc)
        with self.assertRaises(ValidationError):
            BagDisc.objects.create(collection=self.collection, disc=disc)


class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.password = 'strong-pass-123'
        self.user = User.objects.create_user(username='alice', password=self.password)
        self.collection = Collection.objects.create(user=self.user)

    def _disc_payload(self):
        return {
            'name': 'Teebird',
            'manufacturer': 'Innova',
            'plastic': 'Champion',
            'weight': '175.00',
            'color': 'Blue',
            'acquired_at': '2026-03-08T12:00',
        }

    def test_register_creates_user_and_collection(self):
        response = self.client.post(
            reverse('register'),
            {
                'username': 'newuser',
                'first_name': 'New',
                'last_name': 'User',
                'email': 'new@example.com',
                'password1': 'new-strong-pass-123',
                'password2': 'new-strong-pass-123',
            },
        )

        self.assertRedirects(response, reverse('home'))
        created = User.objects.get(username='newuser')
        self.assertTrue(Collection.objects.filter(user=created).exists())

    def test_profile_requires_login(self):
        response = self.client.get(reverse('profile'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('profile')}")

    def test_disc_create_with_in_bag_creates_bag_entry(self):
        self.client.login(username=self.user.username, password=self.password)

        response = self.client.post(
            reverse('disc_create'),
            {**self._disc_payload(), 'in_bag': 'on'},
        )

        self.assertRedirects(response, reverse('my_discs'))
        disc = Disc.objects.get(collection=self.collection, name='Teebird')
        self.assertTrue(BagDisc.objects.filter(collection=self.collection, disc=disc).exists())

    def test_disc_update_can_remove_from_bag(self):
        self.client.login(username=self.user.username, password=self.password)
        disc = Disc.objects.create(
            collection=self.collection,
            name='River',
            manufacturer='Latitude 64',
            plastic='Opto',
            weight=Decimal('174.00'),
            color='Red',
            acquired_at=timezone.now(),
        )
        BagDisc.objects.create(collection=self.collection, disc=disc)

        response = self.client.post(
            reverse('disc_update', args=[disc.id]),
            self._disc_payload(),
        )

        self.assertRedirects(response, reverse('my_discs'))
        self.assertFalse(BagDisc.objects.filter(collection=self.collection, disc=disc).exists())

    def test_disc_delete_for_other_users_disc_returns_404(self):
        other_user = User.objects.create_user(username='bob', password='strong-pass-123')
        other_collection = Collection.objects.create(user=other_user)
        other_disc = Disc.objects.create(
            collection=other_collection,
            name='Wraith',
            manufacturer='Innova',
            plastic='Star',
            weight=Decimal('175.00'),
            color='Orange',
            acquired_at=timezone.now(),
        )

        self.client.login(username=self.user.username, password=self.password)
        response = self.client.post(reverse('disc_delete', args=[other_disc.id]))
        self.assertEqual(response.status_code, 404)

    def test_player_collection_creates_missing_collection(self):
        user_without_collection = User.objects.create_user(username='charlie', password='strong-pass-123')
        self.assertFalse(Collection.objects.filter(user=user_without_collection).exists())

        response = self.client.get(reverse('player_collection', args=[user_without_collection.username]))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Collection.objects.filter(user=user_without_collection).exists())

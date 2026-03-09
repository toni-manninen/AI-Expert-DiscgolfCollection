"""Unit tests for the collection app.

The suite validates model behavior, form validation, and view-level
integrations with emphasis on edge-case inputs.
"""

from datetime import datetime, timedelta, timezone as dt_timezone
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from .forms import DiscForm
from .models import BagDisc, Collection, Disc


class ModelUnitTests(TestCase):
    """Model-level unit tests for Collection, Disc, and BagDisc."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='alice',
            password='strong-pass-123',
        )
        self.collection = Collection.objects.create(user=self.user)

    def test_collection_str_returns_username_collection(self):
        """Collection string representation should include the username."""
        self.assertEqual(str(self.collection), 'alice collection')

    def test_disc_str_supports_unicode_characters(self):
        """Disc string representation should handle Chinese and Arabic text."""
        disc = Disc.objects.create(
            collection=self.collection,
            name='飞盘 قرص',
            manufacturer='制造商 الشركة',
            plastic='ESP',
            weight=Decimal('176.00'),
            color='Blue',
            acquired_at=timezone.now(),
        )

        self.assertEqual(str(disc), '飞盘 قرص (制造商 الشركة)')

    def test_disc_ordering_by_acquired_at_desc_then_name(self):
        """Disc ordering should be newest first and then by name."""
        now = timezone.now()
        first_by_name = Disc.objects.create(
            collection=self.collection,
            name='Alpha',
            manufacturer='Axiom',
            plastic='Neutron',
            weight=Decimal('173.00'),
            color='White',
            acquired_at=now,
        )
        second_by_name = Disc.objects.create(
            collection=self.collection,
            name='Beta',
            manufacturer='Axiom',
            plastic='Neutron',
            weight=Decimal('174.00'),
            color='Black',
            acquired_at=now,
        )
        older = Disc.objects.create(
            collection=self.collection,
            name='Older',
            manufacturer='Innova',
            plastic='Star',
            weight=Decimal('175.00'),
            color='Red',
            acquired_at=now - timedelta(days=1),
        )

        discs = list(Disc.objects.filter(collection=self.collection))
        self.assertEqual(discs, [first_by_name, second_by_name, older])

    def test_bag_disc_rejects_disc_from_other_collection(self):
        """BagDisc should raise validation error for foreign collection discs."""
        other_user = User.objects.create_user(
            username='bob',
            password='strong-pass-123',
        )
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

    def test_bag_disc_unique_constraint_per_collection(self):
        """Same disc cannot be added to the same bag twice."""
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


class DiscFormUnitTests(TestCase):
    """Form-level validation tests for DiscForm edge cases."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='form-user',
            password='strong-pass-123',
        )
        self.collection = Collection.objects.create(user=self.user)

    def _valid_form_data(self):
        return {
            'name': 'Teebird',
            'manufacturer': 'Innova',
            'plastic': 'Champion',
            'weight': '175.00',
            'color': 'Blue',
            'acquired_at': '2026-03-08T12:00',
            'in_bag': 'on',
        }

    def test_disc_form_accepts_chinese_and_arabic_characters(self):
        """Form should be valid with multilingual Unicode values."""
        form_data = self._valid_form_data()
        form_data['name'] = '飞盘 سريع'
        form_data['manufacturer'] = '制造商 الشركة'
        form_data['plastic'] = '塑料 بلاستيك'
        form_data['color'] = '蓝色 أزرق'

        form = DiscForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_disc_form_rejects_very_long_strings(self):
        """Form should reject strings that exceed CharField max_length values."""
        form_data = self._valid_form_data()
        form_data['name'] = 'N' * 121
        form_data['manufacturer'] = 'M' * 121
        form_data['plastic'] = 'P' * 81
        form_data['color'] = 'C' * 61

        form = DiscForm(data=form_data)

        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertIn('manufacturer', form.errors)
        self.assertIn('plastic', form.errors)
        self.assertIn('color', form.errors)

    def test_disc_form_rejects_infinite_weight_values(self):
        """Form should reject positive and negative infinite floats."""
        for value in ('inf', '-inf', 'Infinity', '-Infinity'):
            with self.subTest(weight=value):
                form_data = self._valid_form_data()
                form_data['weight'] = value
                form = DiscForm(data=form_data)

                self.assertFalse(form.is_valid())
                self.assertIn('weight', form.errors)

    def test_disc_form_formats_instance_datetime_for_html_widget(self):
        """Editing form should format acquired_at for datetime-local input."""
        disc = Disc.objects.create(
            collection=self.collection,
            name='Fuse',
            manufacturer='Latitude 64',
            plastic='Opto',
            weight=Decimal('177.00'),
            color='Yellow',
            acquired_at=datetime(2026, 1, 1, 10, 15, tzinfo=dt_timezone.utc),
        )

        form = DiscForm(instance=disc)
        self.assertEqual(form.initial['acquired_at'], '2026-01-01T10:15')


class ViewUnitTests(TestCase):
    """View-level tests covering auth and edge-case payload handling."""

    def setUp(self):
        self.client = Client()
        self.password = 'strong-pass-123'
        self.user = User.objects.create_user(
            username='alice',
            password=self.password,
        )
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
        """Successful registration should create user and collection."""
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
        """Profile endpoint should require authentication."""
        response = self.client.get(reverse('profile'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('profile')}")

    def test_disc_create_with_in_bag_creates_bag_entry(self):
        """Creating a disc with in_bag selected should create BagDisc."""
        self.client.login(username=self.user.username, password=self.password)

        response = self.client.post(
            reverse('disc_create'),
            {**self._disc_payload(), 'in_bag': 'on'},
        )

        self.assertRedirects(response, reverse('my_discs'))
        disc = Disc.objects.get(collection=self.collection, name='Teebird')
        self.assertTrue(
            BagDisc.objects.filter(collection=self.collection, disc=disc).exists()
        )

    def test_disc_create_supports_unicode_payload(self):
        """Disc creation view should persist Chinese and Arabic characters."""
        self.client.login(username=self.user.username, password=self.password)
        payload = self._disc_payload()
        payload['name'] = '飞盘 قرص'
        payload['manufacturer'] = '制造商 الشركة'
        payload['plastic'] = '塑料 بلاستيك'
        payload['color'] = '蓝色 أزرق'

        response = self.client.post(reverse('disc_create'), payload)

        self.assertRedirects(response, reverse('my_discs'))
        self.assertTrue(
            Disc.objects.filter(
                collection=self.collection,
                name='飞盘 قرص',
                manufacturer='制造商 الشركة',
            ).exists()
        )

    def test_disc_create_rejects_very_long_strings(self):
        """Disc creation should not persist when max_length constraints fail."""
        self.client.login(username=self.user.username, password=self.password)
        payload = self._disc_payload()
        payload['name'] = 'N' * 121

        response = self.client.post(reverse('disc_create'), payload)

        self.assertEqual(response.status_code, 200)
        self.assertIn('name', response.context['form'].errors)
        self.assertFalse(Disc.objects.filter(collection=self.collection).exists())

    def test_disc_create_rejects_infinite_weight_values(self):
        """Disc creation should reject both positive and negative infinity."""
        self.client.login(username=self.user.username, password=self.password)

        for value in ('inf', '-inf'):
            with self.subTest(weight=value):
                payload = self._disc_payload()
                payload['weight'] = value

                response = self.client.post(reverse('disc_create'), payload)

                self.assertEqual(response.status_code, 200)
                self.assertIn('weight', response.context['form'].errors)

        self.assertFalse(Disc.objects.filter(collection=self.collection).exists())

    def test_disc_update_can_remove_from_bag(self):
        """Disc update should remove BagDisc when in_bag is not provided."""
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
        """Users should not be able to delete another user's disc."""
        other_user = User.objects.create_user(
            username='bob',
            password='strong-pass-123',
        )
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
        """Public player collection view should create missing collection."""
        user_without_collection = User.objects.create_user(
            username='charlie',
            password='strong-pass-123',
        )
        self.assertFalse(Collection.objects.filter(user=user_without_collection).exists())

        response = self.client.get(
            reverse('player_collection', args=[user_without_collection.username])
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Collection.objects.filter(user=user_without_collection).exists())

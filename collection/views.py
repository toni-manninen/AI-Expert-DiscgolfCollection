from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render

from .forms import DiscForm, LoginForm, RegisterForm
from .models import BagDisc, Collection, Disc


def _ensure_collection(user):
    collection, _ = Collection.objects.get_or_create(user=user)
    return collection


def home(request):
    players = User.objects.all().annotate(
        disc_total=Count('collection__discs', distinct=True),
        bag_total=Count('collection__bag_discs', distinct=True),
    ).order_by('username')
    return render(request, 'collection/home.html', {'players': players})


def register(request):
    if request.user.is_authenticated:
        return redirect('home')

    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        _ensure_collection(user)
        login(request, user)
        messages.success(request, 'Tili luotu onnistuneesti.')
        return redirect('home')

    return render(request, 'collection/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        messages.success(request, 'Kirjautuminen onnistui.')
        return redirect('home')

    return render(request, 'collection/login.html', {'form': form})


@login_required
def profile(request):
    collection = _ensure_collection(request.user)
    context = {
        'collection': collection,
        'disc_total': collection.discs.count(),
        'bag_total': collection.bag_discs.count(),
    }
    return render(request, 'collection/profile.html', context)


@login_required
def my_discs(request):
    collection = _ensure_collection(request.user)
    discs = collection.discs.all()
    bag_disc_ids = set(collection.bag_discs.values_list('disc_id', flat=True))
    return render(
        request,
        'collection/my_discs.html',
        {'collection': collection, 'discs': discs, 'bag_disc_ids': bag_disc_ids},
    )


@login_required
def disc_create(request):
    collection = _ensure_collection(request.user)
    form = DiscForm(request.POST or None, request.FILES or None)

    if request.method == 'POST' and form.is_valid():
        disc = form.save(commit=False)
        disc.collection = collection
        disc.save()

        if form.cleaned_data.get('in_bag'):
            BagDisc.objects.get_or_create(collection=collection, disc=disc)

        messages.success(request, 'Kiekko lisatty kokoelmaan.')
        return redirect('my_discs')

    return render(request, 'collection/disc_form.html', {'form': form, 'title': 'Lisaa kiekko'})


@login_required
def disc_update(request, disc_id):
    collection = _ensure_collection(request.user)
    disc = get_object_or_404(Disc, id=disc_id, collection=collection)
    is_in_bag = BagDisc.objects.filter(collection=collection, disc=disc).exists()
    form = DiscForm(
        request.POST or None,
        request.FILES or None,
        instance=disc,
        initial={'in_bag': is_in_bag},
    )

    if request.method == 'POST' and form.is_valid():
        disc = form.save()
        should_be_in_bag = form.cleaned_data.get('in_bag')

        if should_be_in_bag:
            BagDisc.objects.get_or_create(collection=collection, disc=disc)
        else:
            BagDisc.objects.filter(collection=collection, disc=disc).delete()

        messages.success(request, 'Kiekon tiedot paivitetty.')
        return redirect('my_discs')

    return render(request, 'collection/disc_form.html', {'form': form, 'title': 'Muokkaa kiekkoa'})


@login_required
def disc_delete(request, disc_id):
    collection = _ensure_collection(request.user)
    disc = get_object_or_404(Disc, id=disc_id, collection=collection)

    if request.method == 'POST':
        disc.delete()
        messages.success(request, 'Kiekko poistettu kokoelmasta.')
        return redirect('my_discs')

    return render(request, 'collection/disc_confirm_delete.html', {'disc': disc})


@login_required
def my_bag(request):
    collection = _ensure_collection(request.user)
    bag_items = collection.bag_discs.select_related('disc')
    return render(
        request,
        'collection/my_bag.html',
        {'collection': collection, 'bag_items': bag_items},
    )


def player_collection(request, username):
    player = get_object_or_404(User, username=username)
    collection = _ensure_collection(player)
    return render(
        request,
        'collection/player_collection.html',
        {'player': player, 'collection': collection, 'discs': collection.discs.all()},
    )


def player_bag(request, username):
    player = get_object_or_404(User, username=username)
    collection = _ensure_collection(player)
    bag_items = collection.bag_discs.select_related('disc')
    return render(
        request,
        'collection/player_bag.html',
        {'player': player, 'collection': collection, 'bag_items': bag_items},
    )


@login_required
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'Kirjauduit ulos.')
    return redirect('home')

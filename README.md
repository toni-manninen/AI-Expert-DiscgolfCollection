# DiscgolfCollection

Django-sovellus frisbeegolfkokoelman hallintaan. Sovelluksessa kayttaja voi rekisteroitya, hallita omaa kiekkokokoelmaa, merkitsemaan kiekkoja bakiin ja tarkastella muiden pelaajien julkisia kokoelmia.

## Sisalto

1. [Yhteenveto](#yhteenveto)
2. [Ominaisuudet](#ominaisuudet)
3. [Arkkitehtuuri](#arkkitehtuuri)
4. [Tietomalli](#tietomalli)
5. [URLit ja kayttotapaukset](#urlit-ja-kayttotapaukset)
6. [Projektirakenne](#projektirakenne)
7. [Asennus ja kaynnistys](#asennus-ja-kaynnistys)
8. [Testaus](#testaus)
9. [Hallintakomento: testidata](#hallintakomento-testidata)
10. [Admin-kayttoliittyma](#admin-kayttoliittyma)
11. [Media ja staattiset tiedostot](#media-ja-staattiset-tiedostot)
12. [Turvallisuus ja tuotantoon vienti](#turvallisuus-ja-tuotantoon-vienti)
13. [Tunnetut rajoitteet](#tunnetut-rajoitteet)
14. [Jatkokehitysideoita](#jatkokehitysideoita)

## Yhteenveto

Projekti koostuu yhdesta Django-sovelluksesta (`collection`) ja projektitasoisista asetuksista (`DiscgolfCollection`).

Keskeinen toimintamalli:

- Jokaisella kayttajalla on yksi `Collection`.
- `Collection` sisaltaa useita `Disc`-olioita.
- `BagDisc` kuvaa, mitka kiekot ovat mukana bagissa.
- Julkiset sivut nayttavat pelaajien kokoelman ja bagin ilman kirjautumista.
- Oman datan muokkaus vaatii kirjautumisen.

## Ominaisuudet

- Rekisterointi, kirjautuminen ja uloskirjautuminen.
- Oma profiilisivu (kayttajatiedot + laskurit).
- Omat kiekot: listaus, lisays, muokkaus, poisto.
- Kiekon merkitseminen bakiin lisays- tai muokkausvaiheessa.
- Oma bagin listaus.
- Julkiset pelaajasivut: kokoelma ja bagi.
- Django admin mallien hallintaan.
- Hallintakomento testidatan luontiin.
- Yksikko- ja integraatiotesteja malleille, lomakkeille ja nakymille.

## Arkkitehtuuri

Sovellus noudattaa Django MVT -rakennetta:

- Models: `collection/models.py` (domain-mallit ja validointi).
- Forms: `collection/forms.py` (rekisterointi-, kirjautumis- ja kiekkolomakkeet).
- Views: `collection/views.py` (pyyntojen kasittely, autentikointi, viestit, renderointi).
- Templates: `templates/collection/*.html` (kayttoliittyman sivut).
- URLs: `collection/urls.py` ja `DiscgolfCollection/urls.py` (reititys sovelluksen nakymiin).

## Tietomalli

Mallit sijaitsevat tiedostossa `collection/models.py`.

### Collection

- `user`: `OneToOneField` kayttajaan
- `created_at`: luontiaika

Tarkoitus: yksi kokoelma per kayttaja.

### Disc

- `collection`: viittaus omistavaan kokoelmaan
- `name`, `manufacturer`, `plastic`, `weight`, `color`
- `image`: vapaaehtoinen kuva (`ImageField`)
- `acquired_at`: hankinta-aika

Jarjestys (`Meta.ordering`): uusin ensin (`-acquired_at`), sitten nimi.

### BagDisc

- `collection`: minka kayttajan bagiin rivi kuuluu
- `disc`: viitattu kiekko
- `added_at`: lisausaika

Validointi:

- Uniikkiusrajoite estaa saman kiekon lisaamisen samaan bagiin kahdesti.
- `clean()` varmistaa, etta kiekko kuuluu samaan kokoelmaan kuin bag-rivi.

## URLit ja kayttotapaukset

Reitit maaritellaan tiedostossa `collection/urls.py`.

### Julkiset sivut

- `GET /` etusivu, pelaajalista + laskurit.
- `GET /players/<username>/collection/` pelaajan kokoelma.
- `GET /players/<username>/bag/` pelaajan bag.

### Autentikointi

- `GET/POST /register/` uuden kayttajan luonti.
- `GET/POST /login/` kirjautuminen.
- `POST /logout/` uloskirjautuminen.

### Kirjautumista vaativat sivut

- `GET /profile/` oma profiili.
- `GET /my-discs/` omat kiekot.
- `GET/POST /my-discs/add/` kiekon lisays.
- `GET/POST /my-discs/<disc_id>/edit/` kiekon muokkaus.
- `GET/POST /my-discs/<disc_id>/delete/` kiekon poisto.
- `GET /my-bag/` oma bag.

## Projektirakenne

```text
DiscgolfCollection/
	manage.py
	db.sqlite3
	DiscgolfCollection/
		settings.py
		urls.py
		asgi.py
		wsgi.py
	collection/
		models.py
		forms.py
		views.py
		urls.py
		admin.py
		tests.py
		management/commands/create_test_data.py
		migrations/
		static/collection/styles.css
	templates/collection/
		base.html
		home.html
		register.html
		login.html
		profile.html
		my_discs.html
		disc_form.html
		disc_confirm_delete.html
		my_bag.html
		player_collection.html
		player_bag.html
```

## Asennus ja kaynnistys

Ohjeet on kirjoitettu Windows PowerShell -ymparistolle.

1. Siirry projektin juureen:

```powershell
cd c:\projektit\python\DiscGolfCollection\DiscgolfCollection
```

2. Luo ja aktivoi virtuaaliymparisto:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Asenna riippuvuudet:

```powershell
pip install django pillow
```

4. Aja migraatiot:

```powershell
python manage.py migrate
```

5. Luo admin-kayttaja (valinnainen, suositeltu):

```powershell
python manage.py createsuperuser
```

6. Kaynnista kehityspalvelin:

```powershell
python manage.py runserver
```

Sovellus avautuu osoitteessa `http://127.0.0.1:8000/`.

## Testaus

Kaikki testit:

```powershell
python manage.py test
```

Vain collection-sovellus:

```powershell
python manage.py test collection
```

Testit sijaitsevat tiedostossa `collection/tests.py` ja kattavat erityisesti:

- mallien `__str__`, jarjestys ja `BagDisc`-validointi
- `DiscForm`-validoinnit (myos reunatapauksia)
- nakymien autentikointi, oikeudet, lomakekasittely ja unicode-syotteet

## Hallintakomento: testidata

Komento: `create_test_data`

```powershell
python manage.py create_test_data
```

Mukautetut tunnukset:

```powershell
python manage.py create_test_data --username test_user --password test12345
```

Mita komento tekee:

- luo kayttajan, jos sita ei ole
- luo kayttajan kokoelman, jos sita ei ole
- poistaa aiemmat testikiekot kyseisesta kokoelmasta
- luo 20 kiekkoa valmiista mallista
- lisaa 8 ensimmaista bagiin

Komento on idempotentti saman kayttajan kohdalla.

## Admin-kayttoliittyma

Admin löytyy osoitteesta `/admin/`.

`collection/admin.py` sisaltaa:

- `CollectionAdmin` + sisaiset taulukot kiekoille ja bagiriveille
- `DiscAdmin` suodatuksilla ja hauilla
- `BagDiscAdmin` suodatuksilla ja hauilla

Adminissa on kaytossa listaukset, hakukentat ja lajittelut, jotka tukevat datan huoltoa.

## Media ja staattiset tiedostot

`settings.py`:

- `STATIC_URL = 'static/'`
- `MEDIA_URL = 'media/'`
- `MEDIA_ROOT = BASE_DIR / 'media'`

Kehitystilassa (`DEBUG=True`) projektin URL-konfiguraatio palvelee mediaa automaattisesti.

Staattiset tyylit:

- `collection/static/collection/styles.css`

## Turvallisuus ja tuotantoon vienti

Nykyasetukset ovat kehityskayttoon. Ennen tuotantoa tee ainakin seuraavat muutokset:

- aseta `DEBUG = False`
- siirra `SECRET_KEY` ymparistomuuttujaan
- maarita `ALLOWED_HOSTS`
- konfiguroi staattisten ja media-tiedostojen tuotantopalvelu
- ota kayttoon HTTPS (esim. reverse proxy)
- tarkista tietokantaratkaisu (SQLite -> PostgreSQL tms. kuormitetussa ymparistossa)

## Tunnetut rajoitteet

- Sovellus kayttaa oletuksena SQLite-tietokantaa.
- Kuvakentta (`ImageField`) vaatii toimivan Pillow-asennuksen.
- Python 3.14 + Pillow-yhteensopivuudessa voi ilmeta `_imaging`-ongelma, joka aiheuttaa Django system check -virheen `fields.E210` testien tai komentojen yhteydessa.

Jos kohtaat `fields.E210`-virheen:

- varmista, etta kayttamasi Python-versio ja Pillow-wheel ovat yhteensopivia
- paivita tai vaihda Python/Pillow-versio tarvittaessa

## Jatkokehitysideoita

- Hakutoiminnot ja suodattimet kokoelmaan (valmistaja, muovi, paino, vari).
- Sivutus isoille kokoelmille.
- REST API tai GraphQL mobiili- tai integraatiokayttoon.
- Roolit ja oikeudet (esim. moderaattori/admin-kayttajille laajemmat oikeudet).
- Kiekkokuvatiedostojen validointi ja optimointi.
- CI-putki testien automaattiajoon.

## Lisenssi

Tahan projektiin ei ole viela maaritelty lisenssia.

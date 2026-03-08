# DiscgolfCollection

Django-sovellus frisbeegolfkokoelman hallintaan. Sovelluksessa käyttäjä voi rekisteröityä, lisätä kiekkoja omaan kokoelmaan, ylläpitää bagia ja tarkastella muiden käyttäjien julkisia kokoelmia.

## Ominaisuudet

- Käyttäjän rekisteröinti, kirjautuminen ja uloskirjautuminen
- Oma profiili, josta näkee kiekkojen ja bagin määrän
- Kiekkojen lisäys, muokkaus ja poisto omasta kokoelmasta
- Kiekon merkitseminen bagiin ja poistaminen bagista
- Julkiset näkymät muiden pelaajien kokoelmalle ja bagille
- Hallintakomento testidatan luontiin
- Django-testit mallien ja näkymien keskeisille toiminnoille

## Teknologiat

- Python 3.14
- Django 6
- SQLite (oletustietokanta)

## Projektirakenne

- `DiscgolfCollection/` projektin asetukset ja pääreititys
- `collection/` sovellus: mallit, näkymät, lomakkeet, URLit ja testit
- `templates/` HTML-templatet
- `collection/static/collection/styles.css` tyylit

## Asennus ja käyttöönotto (Windows / PowerShell)

1. Siirry projektin juureen:

```powershell
cd c:\projektit\python\DiscGolfCollection\DiscgolfCollection
```

2. Luo virtuaaliympäristö (jos puuttuu) ja aktivoi se:

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

5. Luo superuser tarvittaessa:

```powershell
python manage.py createsuperuser
```

## Sovelluksen käynnistys

```powershell
python manage.py runserver
```

Avaa selaimessa osoite `http://127.0.0.1:8000/`.

## Testit

Aja kaikki testit:

```powershell
python manage.py test
```

Projektissa on testit tiedostossa `collection/tests.py`.

## Testidatan luonti

Sovelluksessa on hallintakomento, joka luo käyttäjälle testikokoelman (20 kiekkoa, joista 8 bagissa):

```powershell
python manage.py create_test_data
```

Voit antaa myös käyttäjätunnuksen ja salasanan:

```powershell
python manage.py create_test_data --username test_user --password test12345
```

Komento on idempotentti: se käyttää olemassa olevaa käyttäjää/kokoelmaa ja korvaa kyseisen kokoelman aiemmat testikiekot.

## Keskeiset URLit

- `/` etusivu
- `/register/` rekisteröinti
- `/login/` kirjautuminen
- `/profile/` oma profiili
- `/my-discs/` oma kokoelma
- `/my-bag/` oma bag
- `/players/<username>/collection/` pelaajan kokoelma
- `/players/<username>/bag/` pelaajan bag

## Lisenssi

Tähän projektiin ei ole vielä määritelty lisenssiä.

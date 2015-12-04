# Installation

## Allgemeine Vorbereitungen

Mobil bei Uns benötigt einen Root-Server.

Es werden einige Pakete benötigt. Für einen Ubuntu 14.04 Server wären das folgende Pakete:

```
apt-get install libxml2-dev libxslt1-dev
```

Außerdem muss Mobil bei Uns heruntergeladen werden:

```
mkdir /mein/mobil-bei-uns/ordner
cd /mein/mobil-bei-uns/ordner/
git clone https://github.com/OpenRuhr/mobil-bei-uns.git .
```

Des weiteren müss das Virtual Enviroment erstellt werden:

```
cd /mein/mobil-bei-uns/ordner/
virtualenv --no-site-packages venv
source venv/bin/activate
pip install -upgrade pip setuptools
pip install -r requirements.txt
```

## Anbindung des Mobilitäts Daten Marktplatzes MDM

Für die MDM-Anbindung wird ein Zugangszertifikat gebraucht. Dies muss [über die MDM-Website](http://service.mdm-portal.de/mdm-portal-application/) bestellt werden. Man bekommt ein PFX-Zertifikat mit der Endung .p12, welches zunächst aufgesplittet werden muss. Dafür wird das ebenfalls vom MDM-Marktplatz gelieferte Passwort benötigt.

```
cd /mein/mobil-bei-uns/ordner/misc/
openssl pkcs12 -in mein-zertifikat.p12 -nocerts -out mein-zertifikat.enc.key
openssl pkcs12 -in mein-zertifikat.p12 -clcerts -nokeys -out mein-zertifikat.crt
```

Im Header beider generierter Dateien sind einige Bag Attributes, die wir löschen müssen. Anschließend entschlüsseln wir noch den Private Key:

```
openssl rsa -in mein-zertifikat.enc.key -out mein-zertifikat.key
```

Außerdem wird noch die Location Code List benötigt. Diese kann [auf den Seiten des BASt beantragt werden](http://www.bast.de/DE/Verkehrstechnik/Fachthemen/v2-LCL/location-code-list-nutzungsbedingungen.html).


## Datenbank

Anschließend muss die Datenbank initialisiert und migriert werden. Dies geschieht mit Hilfe von Flask-Migrate über das CLI-Interface manage.py :

```
source venv/bin/activate
python manage.py db init
python manage.py db migrate
python manage.py db upgrade
```

## Nutzung

Um die Baustellen von den verschiedenen Quellen abzuholen, wird das Sync-Script aufgerufen:

```
source venv/bin/activate
python manage.py sync
```

Anschließend kann die Webanwendung gestartet werden:

```
source venv/bin/activate
pyton runserver.py
```

Unter http://server-url:5000 kann dann Mobil bei Uns abgerufen werden. Auf einem produktiven Server empfiehlt sich der Einsatz von [gunicorn](http://gunicorn.org/).
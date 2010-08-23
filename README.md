E-Loue
======

Pré-requis
----------

    $ brew install git subversion python pip jpeg postgresl postgis gdal
    $ pip install mercurial virtualenv

Installation
------------

    $ pip install -E env -r deploy/development.txt
    $ source env/bin/activate
  
Usage
-----

Pour avoir un shell :

    $ python manage.py shell``

Pour faire tourner un serveur :

    $ python manage.py runserver

Pour faire tourner les tests :

    $ nosetests

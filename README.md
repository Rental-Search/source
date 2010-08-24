E-Loue
======

Pré-requis
----------

    $ brew install git subversion python pip jpeg postgresl postgis gdal
    $ pip install mercurial virtualenv pyflakes
    
Base de données
---------------

    $ initdb /usr/local/var/postgres
    $ pg_ctl -D /usr/local/var/postgres -l /usr/local/var/postgres/server.log start
    $ createuser --createdb eloue
    $ createlang -d template_postgis plpgsql
    $ psql -d postgres -c "UPDATE pg_database SET datistemplate='true' WHERE datname='template_postgis';"
    $ psql -d template_postgis -f /usr/local/Cellar/postgis/1.5.1/share/postgis/postgis.sql
    $ psql -d template_postgis -f /usr/local/Cellar/postgis/1.5.1/share/postgis/spatial_ref_sys.sql
    $ psql -d template_postgis -c "GRANT ALL ON geometry_columns TO PUBLIC;"
    $ psql -d template_postgis -c "GRANT ALL ON geography_columns TO PUBLIC;"
    $ psql -d template_postgis -c "GRANT ALL ON spatial_ref_sys TO PUBLIC;"
    $ createdb -O eloue -T template_postgis -E UTF-8 eloue

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

    $ python manage.py test

E-Loue
======

Pré-requis
----------

    $ brew install git subversion python pip jpeg libyaml postgresql postgis gdal solr
    $ pip install mercurial virtualenv pyflakes
    
Base de données
---------------

    $ initdb /usr/local/var/postgres
    $ pg_ctl -D /usr/local/var/postgres -l /usr/local/var/postgres/server.log start
    $ createuser --createdb eloue
    $ createdb -E UTF8 template_postgis
    $ createlang -d template_postgis plpgsql
    $ psql -d postgres -c "UPDATE pg_database SET datistemplate='true' WHERE datname='template_postgis';"
    $ psql -d template_postgis -f /usr/local/Cellar/postgis/1.5.1/share/postgis/postgis.sql
    $ psql -d template_postgis -f /usr/local/Cellar/postgis/1.5.1/share/postgis/spatial_ref_sys.sql
    $ psql -d template_postgis -c "GRANT ALL ON geometry_columns TO PUBLIC;"
    $ psql -d template_postgis -c "GRANT ALL ON geography_columns TO PUBLIC;"
    $ psql -d template_postgis -c "GRANT ALL ON spatial_ref_sys TO PUBLIC;"
    $ createdb -O eloue -T template_postgis -E UTF-8 eloue

Moteur de recherche
-------------------

    $ cp solr.war /usr/local/Cellar/solr/1.4.1/example/webapps/
    $ solr `pwd`/deploy/solr/

Installation
------------

    $ pip install -E env -r deploy/development.txt
    $ source env/bin/activate

YUICompressor
-------------
    
    $ wget http://yuilibrary.com/downloads/yuicompressor/yuicompressor-2.4.2.zip
    $ unzip yuicompressor-2.4.2.zip
    $ mkdir -p /usr/local/share/java/
    $ mv yuicompressor-2.4.2/build/yuicompressor-2.4.2.jar /usr/local/share/java/yuicompressor.jar

Usage
-----

Pour avoir un shell :

    $ python eloue/manage.py shell

Pour faire tourner un serveur :

    $ python eloue/manage.py runserver

Pour faire tourner les tests :

    $ python eloue/manage.py test

Pour compresser les javascripts et les css :

    $ python eloue/manage.py syncompress

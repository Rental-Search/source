#!/bin/sh

#export  $(cat .env | grep -v ^# | xargs)
#export DATABASE_URL=postgres://u3en3rb7pcu35:peh2tb6uld4tft4ojmpbbpecf3h@ec2-79-125-13-10.eu-west-1.compute.amazonaws.com:5512/d6ankltapog2na

sudo gunicorn \
  --daemon \
  --error-logfile - \
  --access-logfile - \
  -w 8 \
  -k gevent \
  -b 0.0.0.0:80 \
  --timeout 120 \
  --limit-request-line 0 \
  --limit-request-field_size 0 \
  --forwarded-allow-ips="*" \
  -e DATABASE_URL=postgres://u3en3rb7pcu35:peh2tb6uld4tft4ojmpbbpecf3h@ec2-79-125-13-10.eu-west-1.compute.amazonaws.com:5512/d6ankltapog2na \
  eloue.wsgi

# sudo gunicorn -b 0.0.0.0:80 eloue.wsgi --log-file -

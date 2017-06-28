#!/usr/bin/env bash

# This is run by a cron job to sample the solar production every five minutes.
# */5 * * * * root /usr/local/bin/updatesolar.bash

# The -I option to date specifies ISO 8601 format. The value indicates
# the desired precision.
#
# Oddly enough, this isn't indicated on the man page for the version of
# date I have installed. Equivalent to
#    date +%FT%R%z

# Previously output was sent to /var/log/envoy, but changed because
# /var was filling up. Considered /srv, but /srv is in the same
# partition as /var.

cd /home/pv/envoy
wget \
    --append-output=solar.log \
    --no-cookies \
    --directory-prefix=$(date -Iminute) \
    --adjust-extension \
    --convert-links \
    --page-requisites \
    --execute robots=off \
    --no-parent \
    http://192.168.1.215/home \
    http://192.168.1.215/production

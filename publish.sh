#!/bin/bash
set -e

pipenv run ./create_db.py

pipenv run datasette publish vercel _data/yumyum.db \
    --project yumyum \
    --metadata metadata.yaml \
    --static static:_static \
    --install datasette-block-robots \
    --install datasette-gzip \
    --install datasette-json-html \
    --install datasette-sitemap \
    --install datasette-template-sql \
    --install beautifulsoup4 \
    --plugins-dir _plugins \
    --template-dir _templates \
    --public

#!/usr/bin/env sh
set -e

python manage.py migrate --noinput
python manage.py collectstatic --noinput

if [ -f backend/data/ingredients.json ]; then
  python manage.py load_ingredients --path backend/data/ingredients.json || true
elif [ -f backend/data/ingredients.csv ]; then
  python manage.py load_ingredients --path backend/data/ingredients.csv || true
fi

exec python -m gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 60

#! /usr/bin/env bash

# Let the DB start
python3 /zkit/pre_start.py

exec "$@"

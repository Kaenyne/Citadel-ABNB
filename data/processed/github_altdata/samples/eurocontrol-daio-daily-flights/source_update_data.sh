#!/usr/bin/bash

git add daio_*.csv daio_*.parquet
git commit -m "data update run at $(date +'%FT%X%Z')"
git push

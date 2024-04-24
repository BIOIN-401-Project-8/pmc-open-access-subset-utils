#!/bin/bash

# Run sync.py, archive-pubmed, and archive-nihocc in parallel
docker compose run devcontainer python3 ./src/sync.py --local_path /data/ftp.ncbi.nlm.nih.gov/pub/pmc/oa_bulk &
docker compose run devcontainer /root/edirect/archive-pubmed -index &
docker compose run devcontainer /root/archive-nihocc ‑index &

# Wait for all background jobs to finish
wait

# Run query.py and merge.py sequentially
docker compose run devcontainer python3 ./src/query.py --use_api ./data/rare_diseases.csv /data/pmc-open-access-subset/
docker compose run devcontainer python3 ./src/merge.py /data/pmc-open-access-subset/

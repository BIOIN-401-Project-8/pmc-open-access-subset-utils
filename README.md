# PubMed Central Open Access Subset Utilities

This repository contains a collection of utilities for downloading and querying
the PubMed Central Open Access Subset.

## Prerequisites
1. [Git](https://git-scm.com/downloads)
2. [Docker](https://docs.docker.com/get-docker/)


## Installation

1. `git clone git@github.com:BIOIN-401-Project-8/pmc-open-access-subset-utils.git`
2. `cd pmc-open-access-subset-utils`
3. `docker compose build devcontainer`

## Usage

0. Create a .env file to mount the desired volume. For example, to mount
   `/mnt/deepmind/rd-data` on your local machine to `/data` in the container.
```bash
DATA_PATH=/mnt/deepmind/rd-data
```

1. Bulk download the entire PMC Open Access Subset. This step took 1 hour 35
   minutes and 53 seconds on a fast SSD (write speeds of 5,000 MB/s) and
   requires about 450 GB of disk space.
```bash
docker compose run devcontainer python3 ./src/sync.py --local_path /data/ftp.ncbi.nlm.nih.gov/pub/pmc/oa_bulk
```

Note: In mid-June and mid-December, when new baseline packages are created run the
   sync script will remove the old data and download the new data.

2. Download all PubMed abstracts, this step took 11 hours 13 minutes and 27
seconds. This step requires about 210 GB of disk space.
```bash
docker compose run devcontainer mkdir -p /data/Archive
docker compose run devcontainer /root/edirect/archive-pubmed
```

3. Build a local PubMed search index, this step took ?. This step requires about
210 GB of disk space. This step speeds up the querying process by allowing us to
search the local index instead of querying the PubMed API which has a rate
limit.
```bash
docker compose run devcontainer /root/archive-pubmed -index
docker compose run devcontainer /root/archive-nihocc ‑index
```

4. Run PubMed queries to retrieve relevant PMIDs. This step takes about 2 hours.
This step could be sped up by restricting the queries further or cutting off the
number of articles we are searching for each query. This requires about 82 GB of
disk space.
```bash

docker compose run devcontainer python3 ./src/query.py ./data/rare_diseases.csv /data/pmc-open-access-subset/
```

5. Run the merge script to merge the results of the queries into a single CSV file.
```bash
docker compose run devcontainer python3 ./src/merge.py --output_dir /data/pmc-open-access-subset/
```

6. Setup crontab to run the sync script at 2 am daily.
```bash
crontab -e
# Add the below line to the crontab
0 2 * * * bash ~/Github/bioin-401-project/pmc-open-access-subset-utils/src/sync.sh
```


## Reference

- https://www.ncbi.nlm.nih.gov/books/NBK179288/
- https://www.ncbi.nlm.nih.gov/pmc/tools/ftp/

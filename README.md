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

1. Bulk download the entire PMC Open Access Subset. This step takes about 4 hours on
   a fast SSD (write speeds of 5,100 MB/s). The requires about 499 GB of disk
   space.
```bash
docker compose run devcontainer python3 ./src/sync.py --local_path /data/ftp.ncbi.nlm.nih.gov/pub/pmc/oa_bulk
```

2. Archive PubMed abstracts, this step takes about 2 hours. This step requires
about 200 GB of disk space. This step speeds up the query process by storing
the abstracts locally.
```bash
docker compose run devcontainer bash -c "mkdir -p /data/Archive; ~/edirect/archive-pubmed"
docker compose run devcontainer archive-pubmed -index
```

3. Run PubMed queries to retrieve relevant PMIDs. This step takes about 2 hours.
This step could be sped up by restricting the queries further or cutting off the
number of articles we are searching for each query. This requires about 82 GB of
disk space.
```bash

docker compose run devcontainer python3 ./src/query.py ./data/rare_diseases.csv /data/pmc-open-access-subset/
```

4. Run the merge script to merge the results of the queries into a single CSV file.
```bash
docker compose run devcontainer python3 ./src/merge.py /data/pmc-open-access-subset/
```

5. Setup crontab to run the sync script at 2 am daily.
```bash
crontab -e
# Add the below line to the crontab
0 2 * * * docker compose run devcontainer python3 ./src/sync.py --local_path /data/ftp.ncbi.nlm.nih.gov/pub/pmc/oa_bulk
```

6. Setup crontab to run the query script at 3 am daily.
```bash
crontab -e
# Add the below line to the crontab
0 3 * * * docker compose run devcontainer python3 ./src/query.py ./data/rare_diseases.csv /data/pmc-open-access-subset/
```

7. Setup crontab to run the merge script at 4 am daily.
```bash
crontab -e
# Add the below line to the crontab
0 4 * * * docker compose run devcontainer python3 merge.py /data/pmc-open-access-subset/
```

8. In mid-June and mid-December, when new baseline packages are created run the
   sync script will remove the old data and download the new data.


## Reference

- https://www.ncbi.nlm.nih.gov/books/NBK179288/
- https://www.ncbi.nlm.nih.gov/pmc/tools/ftp/

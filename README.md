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

0. Edit the docker-compose yaml file to mount the desired volume. For example,
   to mount `/data/bioin-401-project` on your local mahine to `/data` in the
   container, add the following to the `docker-compose.yml` file. If you skip
   this step, the data will be stored in the container and will be lost when the
   container is removed.
```yaml
services:
  devcontainer:
    volumes:
      - /data/bioin-401-project:/data:cached
```

1. Bulk download the entire PMC Open Access Subset. This step takes about 4 hours on
   a fast SSD (write speeds of 5,100 MB/s). The requires about 499 GB of disk
   space.
```bash
docker compose run devcontainer python3 ./src/sync.py --local_path /data/ftp.ncbi.nlm.nih.gov/pub/pmc/oa_bulk
```

2. Run PubMed queries to retrieve relevant PMIDs and abstracts. This step takes
about 6 hours. This step could be sped up by restricting the queries further or
cutting off the number of articles we are searching for each query. This requires
about 82 GB of disk space.
```bash

docker compose run devcontainer python3 run_queries.py rare_genetic_disease_names.csv /data/pmc-open-access-subset/
```
3. Setup crontab to run the sync script at 2 am daily.
```bash
crontab -e
# Add the below line to the crontab
0 2 * * * docker compose run devcontainer python3 ./sync.py --local_path /data/ftp.ncbi.nlm.nih.gov/pub/pmc/oa_bulk
```

4. Setup crontab to run the query script at 3 am daily.
```bash
crontab -e
# Add the below line to the crontab
0 3 * * * docker compose run devcontainer python3 run_queries.py rare_genetic_disease_names.csv /data/pmc-open-access-subset/
```

5. In mid-June and mid-December, when new baseline packages are created run the
   sync script will remove the old data and download the new data.


## Reference

https://www.ncbi.nlm.nih.gov/pmc/tools/ftp/

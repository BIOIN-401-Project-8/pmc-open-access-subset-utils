# PubMed Central Open Access Subset Utilities

1. Download the PMC Open Access Subset from the NCBI FTP site
```bash
wget -m ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/oa_bulk/oa_comm/xml/
```
2. Extract the tar files
```bash
python3 untar.py ..data
```
3. Run queries on the PMC Open Access Subset
```bash
python3 run_queries.py rare_genetic_disease_names.csv /data/pmc-open-access-subset/
```
4. Generate plots
```bash
python3 generate_plots.py
```
5. Sync data from PMC Open Access Subset to S3
Use crontab to run this script at 2 am daily
```bash
0 2 * * * python3 ./sync.py
```

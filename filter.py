import glob
import logging
import shutil
from datetime import datetime
from pathlib import Path

import pandas as pd
from tqdm.contrib.concurrent import thread_map

DATA_PATH = Path("/data")
logger = logging.getLogger(__name__)


def load_csvs(csvs):
    dfs = []
    for csv in csvs:
        try:
            df = pd.read_csv(csv)
            df["csv_path"] = csv
            dfs.append(df)
        except UnicodeDecodeError as e:
            logger.exception(csv)
            raise e

    return pd.concat(dfs)


def append_daily_update_to_baseline(baseline_df, daily_update_df):
    df = pd.concat([baseline_df, daily_update_df])
    df = df.drop_duplicates(keep="last")
    return df


def get_pubmed_df():
    baseline_csvs = glob.glob(
        str(DATA_PATH / "ftp.ncbi.nlm.nih.gov/pub/pmc/oa_bulk/oa_*/xml/oa_*_xml.PMC*xxxxxx.baseline.*.filelist.csv")
    )
    baseline_df = load_csvs(baseline_csvs)

    daily_update_csvs = glob.glob(
        str(DATA_PATH / "ftp.ncbi.nlm.nih.gov/pub/pmc/oa_bulk/oa_*/xml/oa_*_xml.incr.*.filelist.csv")
    )
    daily_update_csvs = sorted(daily_update_csvs)
    daily_update_df = load_csvs(daily_update_csvs)
    df = append_daily_update_to_baseline(baseline_df, daily_update_df)
    df = df[df["Retracted"] == "no"]
    df["article_path"] = df["csv_path"].str.split("xml/", 1, expand=True)[0] + "xml/" + df["Article File"]
    return df


def get_efetch_df():
    efetch_csvs = glob.glob(str(DATA_PATH / "pmc-open-access-subset-old/csv/*.csv"))
    efetch_df = load_csvs(efetch_csvs)
    efetch_df.columns = ["query", "PMID", "csv_path"]
    return efetch_df


def copy_article(path, output_dir):
    try:
        shutil.copy(path, output_dir)
    except FileNotFoundError:
        logger.error(path)


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    Path("logs").mkdir(exist_ok=True, parents=True)
    file_handler = logging.FileHandler(f"logs/filter_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logger.info("Loading PubMed dataframe...")
    pubmed_df = get_pubmed_df()
    logger.info("Loading efetch dataframe...")
    efetch_df = get_efetch_df()

    logger.info("Merging PubMed and efetch dataframes...")
    merged_df = pubmed_df.merge(efetch_df, on="PMID", how="right")
    logger.info(f"Saving merged dataframe to {DATA_PATH / 'pmc-open-access-subset/merged.csv'}")
    merged_df.to_csv("/data/pmc-open-access-subset/merged.csv", index=False)

    output_articles_dir = Path(f"/data/pmc-open-access-subset/articles")
    output_articles_dir.mkdir(exist_ok=True, parents=True)

    articles = merged_df["article_path"].dropna().unique()
    logger.info(f"Copying {len(articles)} articles to {output_articles_dir}")
    thread_map(lambda x: copy_article(x, output_articles_dir), articles)


if __name__ == "__main__":
    main()

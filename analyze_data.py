# %%
import glob
import shutil
from pathlib import Path

import pandas as pd
from tqdm.contrib.concurrent import process_map

# %%
DATA_PATH = Path("/data")


# %%
def load_csvs(csvs):
    dfs = [pd.read_csv(csv) for csv in csvs]
    return pd.concat(dfs)


baseline_csvs = glob.glob(
    str(
        DATA_PATH
        / "ftp.ncbi.nlm.nih.gov/pub/pmc/oa_bulk/oa_comm/xml/oa_comm_xml.PMC00*xxxxxx.baseline.2023-12-18.filelist.csv"
    )
)
baseline_df = load_csvs(baseline_csvs)

# %%
daily_update_csvs = glob.glob(
    str(DATA_PATH / "ftp.ncbi.nlm.nih.gov/pub/pmc/oa_bulk/oa_comm/xml/oa_comm_xml.incr.*.filelist.csv")
)
daily_update_df = load_csvs(daily_update_csvs)


# %%
def append_daily_update_to_baseline(baseline_df, daily_update_df):
    df = pd.concat([baseline_df, daily_update_df])
    df = df.drop_duplicates(keep="last")
    return df


df = append_daily_update_to_baseline(baseline_df, daily_update_df)
del baseline_df
del daily_update_df

# %%
df = df[df["Retracted"] == "no"]

# %%
df

# %%
efetch_csvs = glob.glob(str(DATA_PATH / "pmc-open-access-subset/csv/*.csv"))
efetch_df = load_csvs(efetch_csvs)

# %%
efetch_df.columns = ["query", "PMID"]
# %%
efetch_df
# %%
efetch_df_copy = efetch_df[efetch_df["query"] == "STT3A_CDG"].copy()
efetch_df_copy

# %%
df_query = df.merge(efetch_df_copy, on="PMID", how="inner")
df_query

# %%
df_query_found = df_query[(~df_query["query"].isna()) & (~df_query["Article File"].isna())]
len(df_query_found["PMID"].unique())

# %%
df_query_found = df_query[(~df_query["query"].isna())]
len(df_query_found["PMID"].unique())

# %%
print(f"{111588 / 1469797 * 100:.2f}%")

# %%
output_articles_dir = Path("../data/articles")
output_articles_dir.mkdir(exist_ok=True, parents=True)


def copy_article(article_found):
    article_found_path = "../data/ftp.ncbi.nlm.nih.gov/pub/pmc/oa_bulk/oa_comm/xml/" + article_found
    try:
        shutil.copy(article_found_path, output_articles_dir)
    except FileNotFoundError:
        # TODO: raise
        pass


process_map(copy_article, df_query_found["Article File"], max_workers=16)

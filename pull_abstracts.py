import pandas as pd


def get_query_file_name(query: str):
    return "".join(c if c.isalnum() or c in {" ", ".", "_"} else "_" for c in query).rstrip()


query =  "Duchenne muscular dystrophy"
query_file_name = get_query_file_name(query)

# %%
efetch_csv = f"/data/pmc-open-access-subset/csv/{query_file_name}.csv"
efetch_df = pd.read_csv(efetch_csv)

# %%
efetch_df.columns = ["query", "PMID"]
#

# %%
import xml.etree.ElementTree as ET
from pathlib import Path

import tqdm

# %%
def extract_abstracts(path: Path, efetch_df: pd.DataFrame):
    pubmed_article_dir = path / 'efetch/PubmedArticle'
    abstracts = []
    for pmid in tqdm.tqdm(efetch_df["PMID"]):
        pubmed_article_path = pubmed_article_dir / f"{pmid}.xml"
        if not pubmed_article_path.exists():
            abstracts.append(None)
            continue
        tree = ET.parse(pubmed_article_path)
        root = tree.getroot()
        abstract = root.find('MedlineCitation/Article/Abstract/AbstractText')
        if abstract is not None:
            abstract = abstract.text
        abstracts.append(abstract)
    efetch_df["abstract"] = abstracts
    return efetch_df

# %%
efetch_df = extract_abstracts(Path("/data/pmc-open-access-subset"), efetch_df)

# %%
efetch_df.to_csv(query_file_name + ".csv", index=False)
# %%
# percentage of abstracts that are not None
print(f"{efetch_df['abstract'].notna().sum() / len(efetch_df) * 100:.2f}%")

# %%
print(f"{efetch_df['abstract'].notna().sum()} abstracts found")

# %%

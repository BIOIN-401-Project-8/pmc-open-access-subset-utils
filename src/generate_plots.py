# %%
from glob import glob
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from utils import get_esearch_key

# %%
esearchs = glob("/data/pmc-open-access-subset/esearch/*.xml")
dfs = []
for esearch in esearchs:
    esearch_count = get_esearch_key(esearch)
    dfs.append(pd.DataFrame({"count": [esearch_count], "disease": [Path(esearch).stem]}))
df = pd.concat(dfs)
df = df.sort_values("count", ascending=False)
df

# %%
diseases_with_no_articles = df[df["count"] == 0]
n_diseases_with_no_articles = len(diseases_with_no_articles)
percent_diseases_with_no_articles = n_diseases_with_no_articles / len(df) * 100
n_diseases = len(df)
print(
    f"{n_diseases_with_no_articles} / {n_diseases} ({percent_diseases_with_no_articles:.2f}%) "
    "diseases with no articles"
)

# %%
plt.title("Number of Pubmed Articles per Disease")
plt.xlabel("Disease")
plt.bar(range(1, len(df) + 1), df["count"])
plt.ylabel("Number of articles (log scale)")
plt.yscale("log")
plt.show()

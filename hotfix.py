#%%

import pandas as pd


df = pd.read_csv('data/rare_diseases.csv')

from pathlib import Path

def get_query_file_name(query: str):
    return "".join(c if c.isalnum() or c in {" ", ".", "_"} else "_" for c in query).rstrip()


names = set(map(get_query_file_name, df[df.columns[0]]))
for file in Path('/data/pmc-open-access-subset/csv').glob('*.csv'):
    if file.stem not in names:
        print(file.stem)
        file.unlink()

# %%
names
# %%
len(list(Path('/data/pmc-open-access-subset/csv').glob('*.csv')))

# %%

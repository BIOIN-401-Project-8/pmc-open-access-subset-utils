import pandas as pd
from glob import glob
from xml.etree import ElementTree as ET
def get_count(path):
    try:
        tree = ET.parse(path)
    except ET.ParseError:
        return 0
    count = tree.find('Count').text
    return int(count) if count else 0


def main():
    esearchs = glob("output/esearch/*.xml")
    counts = list(map(get_count, esearchs))
    csvs = len(glob("output/csv/*.csv"))
    efetchs = len(glob("output/efetch/PubmedArticleSet/*.xml"))
    df = pd.read_csv("rare_genetic_disease_names.csv")
    total = len(df) - len([c for c in counts if c == 0])
    done = csvs + efetchs
    print(f"{done}/{total} ({done/total*100:.2f}%)")


if __name__ == "__main__":
    main()

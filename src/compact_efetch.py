import argparse
import glob
import logging
import os
import xml.etree.ElementTree as ET
from pathlib import Path

import tqdm

logger = logging.getLogger(__name__)


def extract_pubmed_articles(path: Path, pubmed_article_set_path: str):
    try:
        tree = ET.parse(pubmed_article_set_path)
    except ET.ParseError:
        logger.exception(pubmed_article_set_path)
        return
    root = tree.getroot()

    pubmed_article_dir = path / 'efetch/PubmedArticle'
    pubmed_article_dir.mkdir(parents=True, exist_ok=True)
    csv_dir = path / 'csv'
    csv_dir.mkdir(parents=True, exist_ok=True)

    pubmed_article_stem = Path(pubmed_article_set_path).stem
    csv_path = csv_dir / f"{pubmed_article_stem}.csv"

    if csv_path.exists():
        logger.info(f'{csv_path} exists, skipping')
        return

    with open(csv_path, 'w') as f:
        f.write('pubmed_article_set, pubmed_article\n')

    for pubmed_article in root.findall('PubmedArticle'):
        pmid = pubmed_article.find('MedlineCitation/PMID').text
        pubmed_article_path = pubmed_article_dir / f"{pmid}.xml"
        with open(csv_path, 'a') as f:
            f.write(f'{pubmed_article_stem}, {pmid}\n')
        if pubmed_article_path.exists():
            continue
        with open(pubmed_article_path, 'wb') as f:
            f.write(ET.tostring(pubmed_article))
    Path(pubmed_article_set_path).unlink()


def main():
    parser = argparse.ArgumentParser(description="Compact efetch output")
    parser.add_argument("path", type=str, help="Path to output directory")
    args = parser.parse_args()
    path = Path(args.path)
    pubmed_article_sets = glob.glob(str(path / 'efetch/PubmedArticleSet/*.xml'))
    pubmed_article_sets.sort(key=lambda x: os.path.getsize(x))
    for pubmed_article_set in tqdm.tqdm(pubmed_article_sets):
        extract_pubmed_articles(path, pubmed_article_set)


if __name__ == '__main__':
    main()

import glob
import os
import tqdm
import lxml.etree as ET
from pathlib import Path
import logging

def main():
    pubmed_article_sets = glob.glob('output/efetch/PubmedArticleSet/*.xml')

    pubmed_article_sets.sort(key=lambda x: os.path.getsize(x))
    logger = logging.getLogger(__name__)

    for pubmed_article_set in tqdm.tqdm(pubmed_article_sets):
        try:
            tree = ET.parse(pubmed_article_set)
        except ET.XMLSyntaxError:
            try:
                Path(pubmed_article_set).unlink()
            except FileNotFoundError:
                logger.warning(f'FileNotFoundError: {pubmed_article_set}')
            continue
        root = tree.getroot()

        for pubmed_article in root.findall('PubmedArticle'):
            pmid = pubmed_article.find('MedlineCitation/PMID').text
            pubmed_article_stem = Path(pubmed_article_set).stem
            if not Path(f'output/csv/{pubmed_article_stem}.csv').exists():
                Path(f'output/csv/{pubmed_article_stem}.csv').parent.mkdir(parents=True, exist_ok=True)
                with open(f'output/csv/{pubmed_article_stem}.csv', 'w') as f:
                    f.write('pubmed_article_set, pubmed_article\n')
            with open(f'output/csv/{pubmed_article_stem}.csv', 'a') as f:
                f.write(f'{pubmed_article_stem}, {pmid}\n')
            if Path(f'output/efetch/PubmedArticle/{pmid}.xml').exists():
                continue
            with open(f'output/efetch/PubmedArticle/{pmid}.xml', 'wb') as f:
                f.write(ET.tostring(pubmed_article))
        # delete file
        try:
            Path(pubmed_article_set).unlink()
        except FileNotFoundError:
            logger.warning(f'FileNotFoundError: {pubmed_article_set}')

if __name__ == '__main__':
    main()

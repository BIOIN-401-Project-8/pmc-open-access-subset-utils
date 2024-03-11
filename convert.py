import glob
from pathlib import Path

from bioc import biocxml
from bioconverters import pubmedxml2bioc, pmcxml2bioc
from tqdm import tqdm


def main():
    # rerun this later
    convert_abstracts()
    # this will take 10 hours to run...
    # convert_pmc_xml()


def convert_abstracts():
    pmc_xmls = glob.glob("/data/pmc-open-access-subset/efetch/PubmedArticle/*.xml")
    pmc_bioc_dir = Path("/data/pmc-open-access-subset/abstracts-bioc")
    pmc_bioc_dir.mkdir(exist_ok=True)

    for pmc_xml in tqdm(pmc_xmls):
        path = Path(pmc_xml)
        path_bioc = pmc_bioc_dir / path.with_suffix(".bioc").name
        if path_bioc.exists():
            continue
        doc = next(pubmedxml2bioc(pmc_xml))
        doc.encoding = 'utf-8'
        doc.standalone = True

        with open(str(path_bioc), 'w') as fp:
            biocxml.dump(doc, fp)


def convert_pmc_xml():
    pmc_xmls = glob.glob("/data/pmc-open-access-subset/articles/*.xml")
    pmc_bioc_dir = Path("/data/pmc-open-access-subset/articles-bioc")
    pmc_bioc_dir.mkdir(exist_ok=True)

    for pmc_xml in tqdm(pmc_xmls):
        path = Path(pmc_xml)
        path_bioc = pmc_bioc_dir / path.with_suffix(".bioc").name
        if path_bioc.exists():
            continue
        doc = next(pmcxml2bioc(pmc_xml))
        doc.encoding = 'utf-8'
        doc.standalone = True

        with open(str(path_bioc), 'w') as fp:
            biocxml.dump(doc, fp)


if __name__ == '__main__':
    main()

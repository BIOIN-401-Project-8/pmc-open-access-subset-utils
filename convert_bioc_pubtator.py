import glob
from pathlib import Path

import lxml.etree
from bioc import biocxml, pubtator
from tqdm import tqdm

from src.bioc2pubtator import bioc2pubtator


def convert_abstracts():
    pmc_xmls = glob.glob("/data/pmc-open-access-subset/abstracts-ner/*")
    pmc_pubtator_dir = Path("/data/pmc-open-access-subset/abstracts-pubtator")
    pmc_pubtator_dir.mkdir(exist_ok=True)

    for pmc_xml in tqdm(pmc_xmls):
        path = Path(pmc_xml)
        path_pubtator = pmc_pubtator_dir / path.with_suffix(".pubtator").name
        if path_pubtator.exists():
            continue
        with open(pmc_xml, "rb") as fp:
            try:
                collection = biocxml.load(fp)
            except lxml.etree.XMLSyntaxError:
                continue
        pubdoc = bioc2pubtator(collection.documents[0])
        with open(str(path_pubtator), "w") as fp:
            pubtator.dump([pubdoc], fp)


def main():
    convert_abstracts()


if __name__ == "__main__":
    main()

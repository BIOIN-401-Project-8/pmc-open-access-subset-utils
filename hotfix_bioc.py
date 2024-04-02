import glob
from pathlib import Path

from bioc import biocxml, BioCCollection
from bioconverters import pubmedxml2bioc, pmcxml2bioc
from tqdm import tqdm


def main():
    # rerun this later
    convert_abstracts()
    # this will take 10 hours to run...
    # convert_pmc_xml()


def convert_abstracts():
    pmc_xmls = glob.glob("/data/pmc-open-access-subset/abstracts-ner/*")

    for pmc_xml in tqdm(pmc_xmls):
        path = Path(pmc_xml)
        with open(pmc_xml, "rb") as fp:
            try:
                collection = biocxml.load(fp)
            except:
                continue

        for document in collection.documents:
            for passage in document.passages:
                if passage.infons["section"] == "title":
                    passage.infons["type"] = passage.infons["section"]

        with open(path, 'w') as fp:
            biocxml.dump(collection, fp)


if __name__ == '__main__':
    main()

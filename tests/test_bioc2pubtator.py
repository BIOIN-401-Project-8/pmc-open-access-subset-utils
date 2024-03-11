from pathlib import Path

from bioc import biocxml, pubtator

from src.bioc2pubtator import bioc2pubtator

TEST_DATA = Path(__file__).parent / "data"


def test_bioc2pubtator():
    with open(TEST_DATA / "pubtator3.33333140.xml", "rb") as fp:
        collection = biocxml.load(fp)
    pub = bioc2pubtator(collection.documents[0])
    with open(TEST_DATA / "pubtator3.33333140.txt", "r") as fp:
        assert fp.read() == pubtator.dumps([pub]) + '\n'

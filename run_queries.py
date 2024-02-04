import argparse
import logging
import subprocess
from datetime import datetime
from pathlib import Path

import pandas as pd
from tqdm.contrib.concurrent import thread_map
from xml.etree import ElementTree as ET

def get_count(path):
    try:
        tree = ET.parse(path)
    except ET.ParseError:
        return 0
    except FileNotFoundError:
        return 0
    count = tree.find('Count').text
    return int(count) if count else 0


def get_query_file_name(query: str):
    return "".join(c if c.isalnum() or c in {' ','.','_'} else "_" for c in query).rstrip()

def main():
    parser = argparse.ArgumentParser(description="Run queries on PubMed")
    parser.add_argument("query_csv", type=str, help="Path to CSV file with queries")
    parser.add_argument("output_dir", type=str, help="Path to output directory")
    args = parser.parse_args()

    # log to file and stdout
    logging.basicConfig(
        filename=f"run_queries_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
        filemode="w",
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s"
    )
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)

    df = pd.read_csv(args.query_csv)
    output_dir = Path(args.output_dir)
    esearch_output_dir = output_dir / "esearch"
    esearch_output_dir.mkdir(parents=True, exist_ok=True)
    efetch_output_dir = output_dir / "efetch/PubmedArticleSet"
    efetch_output_dir.mkdir(parents=True, exist_ok=True)
    xtract_output_dir = output_dir / "csv"
    xtract_output_dir.mkdir(parents=True, exist_ok=True)

    length = len(df)

    df["esearch_output_exists"] = df[df.columns[0]].apply(
        lambda query: (esearch_output_dir / f"{get_query_file_name(query)}.xml").exists()
    )

    thread_map(
        lambda iq: run_esearch(
            f"{iq[0]+1}/{length}",
            iq[1],
            esearch_output_dir,
            efetch_output_dir,
            xtract_output_dir
        ),
        list(enumerate(df[~df["esearch_output_exists"]][df.columns[0]])),
        max_workers=5
    )

    # sort df by size of esearch output
    # df["esearch_output_size"] = df[df.columns[0]].apply(
    #     lambda query: get_count(esearch_output_dir / f"{get_query_file_name(query)}.xml")
    # )
    # df = df.sort_values(by="esearch_output_size", ascending=True)
    # df = df[df["esearch_output_size"] > 0]

    # thread_map(
    #     lambda iq: run_efetch(
    #         f"{iq[0]+1}/{length}",
    #         iq[1],
    #         esearch_output_dir,
    #         efetch_output_dir,
    #         xtract_output_dir
    #     ),
    #     list(enumerate(df[df.columns[0]])),
    #     max_workers=5
    # )


def run_esearch(i: str, query: str, esearch_output_dir: Path, efetch_output_dir: Path, xtract_output_dir: Path):
    query_file_name = get_query_file_name(query)
    if query_file_name != query:
        logging.warning(f"Query {query} has been renamed to {query_file_name}")
    esearch_output_xml = esearch_output_dir / f"{query_file_name}.xml"
    efetch_output_xml = efetch_output_dir / f"{query_file_name}.xml"
    xtract_output_csv = xtract_output_dir / f"{query_file_name}.csv"

    # if xtract_output_csv.exists():
    #     return


    if not esearch_output_xml.exists():
        logging.info(f"Running query {i}: {query}")
        with open(esearch_output_xml, "w") as f:
            subprocess.run(
                    [
                        "esearch",
                        "-db",
                        "pubmed",
                        "-query",
                        query
                    ],
                    stdout=f
                )
        if esearch_output_xml.stat().st_size == 0:
            esearch_output_xml.unlink()
            logging.warning(f"Query esearch {query} is empty")
            return

def run_efetch(i: str, query: str, esearch_output_dir: Path, efetch_output_dir: Path, xtract_output_dir: Path):
    query_file_name = "".join(c if c.isalnum() or c in {' ','.','_'} else "_" for c in query).rstrip()
    if query_file_name != query:
        logging.warning(f"Query {query} has been renamed to {query_file_name}")
    esearch_output_xml = esearch_output_dir / f"{query_file_name}.xml"
    efetch_output_xml = efetch_output_dir / f"{query_file_name}.xml"
    xtract_output_csv = xtract_output_dir / f"{query_file_name}.csv"

    if xtract_output_csv.exists():
        return

    logging.info(f"Running query {i}: {query}")
    if esearch_output_xml.exists() and not efetch_output_xml.exists():
        with open(esearch_output_xml, "r") as f, open(efetch_output_xml, "w") as g:
            subprocess.run(
                    [
                        "efetch",
                        "-format",
                        "xml"
                    ],
                    stdin=f,
                    stdout=g
                )
        if efetch_output_xml.stat().st_size == 0:
            # efetch_output_xml.unlink()
            logging.warning(f"Query efetch {query} is empty")
            return

# def run_extract(i: str, query: str, esearch_output_dir: Path, efetch_output_dir: Path, xtract_output_dir: Path):
    # query_file_name = "".join(c if c.isalnum() or c in {' ','.','_'} else "_" for c in query).rstrip()
    # if query_file_name != query:
    #     logging.warning(f"Query {query} has been renamed to {query_file_name}")
    # esearch_output_xml = esearch_output_dir / f"{query_file_name}.xml"
    # efetch_output_xml = efetch_output_dir / f"{query_file_name}.xml"
    # xtract_output_csv = xtract_output_dir / f"{query_file_name}.csv"

    # if xtract_output_csv.exists():
    #     return
    # if efetch_output_xml.exists() and not xtract_output_csv.exists():
    #     with open(xtract_output_csv, "w") as h:
    #         h.write("PMID\n")
    #         h.flush()
    #         subprocess.run(
    #             [
    #                 "xtract",
    #                 "-input",
    #                 efetch_output_xml,
    #                 "-pattern",
    #                 "PubmedArticle",
    #                 "-element",
    #                 "MedlineCitation/PMID"
    #             ],
    #             stdout=h
    #         )
    #     with open(xtract_output_csv, "r") as h:
    #         h.readline()
    #         # if the file is empty, delete it
    #         if not h.readline():
    #             # xtract_output_csv.unlink()
    #             logging.warning(f"Query xtract {query} is empty")
    #             return


if __name__ == "__main__":
    main()

import argparse
import logging
import subprocess
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree as ET

import pandas as pd
from tqdm.contrib.concurrent import thread_map

from compact_efetch import extract_pubmed_articles
from utils import get_esearch_count


def get_query_file_name(query: str):
    return "".join(c if c.isalnum() or c in {" ", ".", "_"} else "_" for c in query).rstrip()


def main():
    parser = argparse.ArgumentParser(description="Run queries on PubMed")
    parser.add_argument("query_csv", type=str, help="Path to CSV file with queries")
    parser.add_argument("output_dir", type=str, help="Path to output directory")
    args = parser.parse_args()

    logging.basicConfig(
        filename=f"run_queries_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
        filemode="w",
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)

    df = pd.read_csv(args.query_csv)
    output_dir = Path(args.output_dir)
    esearch_output_dir = output_dir / "esearch"
    esearch_output_dir.mkdir(parents=True, exist_ok=True)
    efetch_output_dir = output_dir / "efetch/PubmedArticleSet"
    efetch_output_dir.mkdir(parents=True, exist_ok=True)
    csv_output_dir = output_dir / "csv"
    csv_output_dir.mkdir(parents=True, exist_ok=True)

    df["esearch_output_exists"] = df[df.columns[0]].apply(
        lambda query: (esearch_output_dir / f"{get_query_file_name(query)}.xml").exists()
    )
    df_to_esearch = df[~df["esearch_output_exists"]][df.columns[0]]
    print(f"Running esearch for {len(df_to_esearch)} queries")

    thread_map(
        lambda query: run_esearch(query, esearch_output_dir),
        df_to_esearch,
        max_workers=5,
    )

    # sort df by size of esearch output
    df["esearch_output_size"] = df[df.columns[0]].apply(
        lambda query: get_esearch_count(esearch_output_dir / f"{get_query_file_name(query)}.xml")
    )
    df = df.sort_values(by="esearch_output_size", ascending=True)
    df = df[df["esearch_output_size"] > 0]
    df["csv_output_exists"] = df[df.columns[0]].apply(
        lambda query: (csv_output_dir / f"{get_query_file_name(query)}.csv").exists()
    )

    df_to_efetch = df[~df["csv_output_exists"]][df.columns[0]]
    print(f"Running efetch for {len(df_to_efetch)} queries")

    thread_map(
        lambda query: run_efetch(
            query,
            output_dir,
            esearch_output_dir,
            efetch_output_dir
        ),
        df_to_efetch,
        max_workers=5
    )


def run_esearch(query: str, esearch_output_dir: Path):
    query_file_name = get_query_file_name(query)
    esearch_output_xml = esearch_output_dir / f"{query_file_name}.xml"

    logging.info(f"Running esearch for {query}")
    output = subprocess.run(
        ["esearch", "-db", "pubmed", "-query", query],
        capture_output=True,
        text=True,
    )
    if output.returncode != 0:
        logging.warning(f"Query esearch {query} failed")
        logging.warning(output.stderr)
        return
    with open(esearch_output_xml, "w") as f:
        f.write(output.stdout)


def run_efetch(query: str, output_dir: Path, esearch_output_dir: Path, efetch_output_dir: Path):
    query_file_name = get_query_file_name(query)
    esearch_output_xml = esearch_output_dir / f"{query_file_name}.xml"
    efetch_output_xml = efetch_output_dir / f"{query_file_name}.xml"

    logging.info(f"Running efetch for {query}")
    output = subprocess.run(
        ["efetch", "-db", "pubmed", "-format", "xml", "-input", esearch_output_xml],
        capture_output=True,
        text=True,
    )
    if output.returncode != 0:
        logging.warning(f"Query efetch {query} failed")
        logging.warning(output.stderr)
        return
    with open(efetch_output_xml, "w") as f:
        f.write(output.stdout)

    logging.info(f"Extracting articles for {query}")
    extract_pubmed_articles(output_dir, efetch_output_xml)


if __name__ == "__main__":
    main()

import argparse
import logging
import subprocess
from datetime import datetime
from pathlib import Path

import pandas as pd
from tqdm.contrib.concurrent import process_map, thread_map

from utils import get_esearch_key

logger = logging.getLogger(__name__)


def get_query_file_name(query: str):
    return "".join(c if c.isalnum() or c in {" ", ".", "_"} else "_" for c in query).rstrip()


def main():
    parser = argparse.ArgumentParser(description="Run queries on PubMed")
    parser.add_argument("query_csv", type=str, help="Path to CSV file with queries")
    parser.add_argument("output_dir", type=str, help="Path to output directory")
    args = parser.parse_args()

    logging.basicConfig(
        filename=f"logs/query_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
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
    csv_output_dir = output_dir / "csv"
    csv_output_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Running esearch for {len(df)} queries")

    thread_map(lambda query: run_esearch(query, esearch_output_dir), df[df.columns[0]])

    # sort df by size of esearch output
    df["esearch_output_size"] = df[df.columns[0]].apply(
        lambda query: get_esearch_key((esearch_output_dir / f"{get_query_file_name(query)}.xml").read_text()) if (esearch_output_dir / f"{get_query_file_name(query)}.xml").exists() else 0
    )
    df = df.sort_values(by="esearch_output_size", ascending=True)
    df = df[df["esearch_output_size"] > 0]
    df["csv_output_exists"] = df[df.columns[0]].apply(
        lambda query: (csv_output_dir / f"{get_query_file_name(query)}.csv").exists()
    )

    df_to_efetch = df[~df["csv_output_exists"]][df.columns[0]]
    logger.info(f"Running efetch for {len(df_to_efetch)} queries")

    thread_map(lambda query: run_efetch(query, esearch_output_dir, csv_output_dir), df_to_efetch, max_workers=8)


def run_esearch(query: str, esearch_output_dir: Path):
    query_file_name = get_query_file_name(query)
    esearch_output_xml = esearch_output_dir / f"{query_file_name}.xml"

    args = ["esearch", "-db", "pubmed", "-query", query]
    logging.info(" ".join(args))
    output = subprocess.run(
        args,
        capture_output=True,
        text=True,
    )
    if output.returncode != 0:
        logging.warning(f"Query esearch {query} failed")
        logging.warning(output.stderr)
        return
    with open(esearch_output_xml, "w") as f:
        f.write(output.stdout)


def run_efetch(query: str, esearch_output_dir: Path, csv_output_dir: Path):
    query_file_name = get_query_file_name(query)
    esearch_output_xml = esearch_output_dir / f"{query_file_name}.xml"
    output_csv = csv_output_dir / f"{query_file_name}.csv"

    logging.info(f"Running efetch for {query}")
    while True:
        with open(esearch_output_xml, "r") as f:
            esearch_output = f.read()
            p = subprocess.Popen(
                ["efetch", "-format", "uid"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            output = p.communicate(input=esearch_output)
        if p.returncode != 0:
            logging.warning(f"Query efetch {query} failed")
            logging.warning(output[1])
        csv = output[0]
        if csv:
            break
        else:
            logging.warning(f"Empty efetch output for {query}")

    with open(output_csv, "w") as f:
        f.write('PMID\n')
        f.write(csv)


if __name__ == "__main__":
    main()
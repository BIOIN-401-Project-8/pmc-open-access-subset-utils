import argparse
import asyncio
import glob
import logging
import re
import subprocess
import tempfile
import urllib.request
from asyncio import Semaphore
from datetime import date, datetime
from pathlib import Path

import aiofiles
import aiohttp
from tqdm import tqdm
from tqdm.asyncio import tqdm_asyncio

logger = logging.getLogger(__name__)


async def sync_baselines(ftp_path: str, local_path: str, group: str):
    local_csvs = get_local_baselines(local_path, group)
    remote_csvs = get_remote_baselines(ftp_path, group)
    csvs_delta = sorted(set(remote_csvs) - set(local_csvs))
    targz_delta = [csv.replace("filelist.csv", "tar.gz") for csv in csvs_delta]
    logger.info(f"CSVs delta: {csvs_delta}")
    if not csvs_delta:
        logger.info(f"Already up to date for group {group} baselines")
    else:
        Path(f"{local_path}/oa_{group}/xml").unlink(missing_ok=True)

    sem = Semaphore(1)
    await tqdm_asyncio.gather(
        *[
            sync_baseline(ftp_path, local_path, group, csv, targz, sem)
            for csv, targz in list(zip(csvs_delta, targz_delta))
        ]
    )


async def sync_baseline(ftp_path: str, local_path: str, group: str, csv: str, targz: str, sem: Semaphore):
    with tempfile.NamedTemporaryFile() as tmp:
        url = f"{ftp_path}/oa_{group}/xml/{targz}"
        timeout = aiohttp.ClientTimeout(total=None)
        async with sem, aiohttp.ClientSession(timeout=timeout) as session:
            logger.info(f"{url} -> {tmp.name}")
            async with session.get(url) as resp:
                if resp.status == 200:
                    async with aiofiles.open(tmp.name, mode="wb") as f:
                        async for chunk in resp.content.iter_any():
                            await f.write(chunk)
                else:
                    raise Exception(f"Failed to download {url}")
        Path(f"{local_path}/oa_{group}/xml/").mkdir(parents=True, exist_ok=True)
        args = ["tar", "-xzvf", tmp.name, "-C", f"{local_path}/oa_{group}/xml/"]
        logger.info(" ".join(args))
        process = await asyncio.create_subprocess_exec(
            *args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            logger.error(stdout)
            logger.error(stderr)
            raise Exception(f"Failed to extract {tmp.name} to {local_path}/oa_{group}/xml/")
    url = f"{ftp_path}/oa_{group}/xml/{csv}"
    filename = f"{local_path}/oa_{group}/xml/{csv}"
    logger.info(f"{url} -> {filename}")
    timeout = aiohttp.ClientTimeout(total=None)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                async with aiofiles.open(filename, mode="wb") as f:
                    await f.write(await resp.read())
            else:
                raise Exception(f"Failed to download {url}")


def get_remote_baselines(ftp_path: str, group: str):
    with urllib.request.urlopen(f"{ftp_path}/oa_{group}/xml/") as response:
        html = response.read().decode("utf-8")
    csvs = re.findall(rf"oa_{group}_xml\..*\.baseline\..*\.filelist\.csv", html)
    csvs = [csv.split(">")[-1] for csv in csvs]
    return csvs


def get_local_baselines(local_path: str, group: str):
    csvs = glob.glob(f"{local_path}/oa_{group}/xml/oa_{group}_xml.*.baseline.*.filelist.csv")
    csvs = [csv.split("/")[-1] for csv in csvs]
    return csvs


async def sync_incr(ftp_path: str, local_path: str, date: str, group: str, sem: Semaphore):
    with tempfile.NamedTemporaryFile() as tmp:
        url = f"{ftp_path}/oa_{group}/xml/oa_{group}_xml.incr.{date}.tar.gz"
        timeout = aiohttp.ClientTimeout(total=None)
        async with sem, aiohttp.ClientSession(timeout=timeout) as session:
            logger.info(f"{url} -> {tmp.name}")
            async with session.get(url) as resp:
                if resp.status == 200:
                    async with aiofiles.open(tmp.name, mode="wb") as f:
                        async for chunk in resp.content.iter_any():
                            await f.write(chunk)
                else:
                    raise Exception(f"Failed to download {url}")
        args = ["tar", "-xzvf", tmp.name, "-C", f"{local_path}/oa_{group}/xml/"]
        logger.info(" ".join(args))
        process = await asyncio.create_subprocess_exec(
            *args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            logger.error(stdout)
            logger.error(stderr)
            raise Exception(f"Failed to extract {tmp.name} to {local_path}/oa_{group}/xml/")
    url = f"{ftp_path}/oa_{group}/xml/oa_{group}_xml.incr.{date}.filelist.csv"
    filename = f"{local_path}/oa_{group}/xml/oa_{group}_xml.incr.{date}.filelist.csv"
    logger.info(f"{url} -> {filename}")
    timeout = aiohttp.ClientTimeout(total=None)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                async with aiofiles.open(filename, mode="wb") as f:
                    await f.write(await resp.read())
            else:
                raise Exception(f"Failed to download {url}")


def get_local_dates(local_path: str, group: str):
    csvs = glob.glob(f"{local_path}/oa_{group}/xml/oa_{group}_xml.incr.*.filelist.csv")
    dates = [date.fromisoformat(csv.split(".")[-3]) for csv in csvs]
    return dates


def get_remote_dates(ftp_path: str, group: str):
    with urllib.request.urlopen(f"{ftp_path}/oa_{group}/xml/") as response:
        html = response.read().decode("utf-8")
    dates = [
        date.fromisoformat(csv)
        for csv in re.findall(rf"oa_{group}_xml\.incr\.(\d{{4}}-\d{{2}}-\d{{2}})\.filelist\.csv", html)
    ]
    return dates


async def sync_incrs(ftp_path: str, local_path: str, group: str):
    local_latest_dates = get_local_dates(local_path, group)
    remote_latest_dates = get_remote_dates(ftp_path, group)
    dates_delta = sorted(set(remote_latest_dates) - set(local_latest_dates))
    if not dates_delta:
        logger.info(f"Already up to date for group {group} incrs")
    else:
        logger.info(f"Dates delta: {dates_delta}")
    sem = Semaphore(1)
    for date in tqdm(dates_delta):
        await sync_incr(ftp_path, local_path, date.isoformat(), group, sem)


def setup_logger(log_path: Path):
    log_path.mkdir(parents=True, exist_ok=True)
    filename = log_path / f"{Path(__file__).stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    logging.basicConfig(
        filename=filename,
        filemode="w",
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logger.addHandler(console)


async def main():
    # TODO: remove code duplication
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--ftp_path",
        type=str,
        default="https://ftp.ncbi.nlm.nih.gov/pub/pmc/oa_bulk",
        help="FTP path to download PMC OA bulk",
    )
    parser.add_argument(
        "--local_path",
        type=str,
        default="/data/ftp.ncbi.nlm.nih.gov/pub/pmc/oa_bulk",
        help="Local path to download PMC OA bulk",
    )
    parser.add_argument(
        "--log_path",
        type=str,
        default="logs",
        help="Path to store logs",
    )
    parser.add_argument(
        "--groups",
        type=str,
        nargs="+",
        default=["comm", "noncomm", "other"],
        help="Groups to download",
    )
    args = parser.parse_args()
    ftp_path = args.ftp_path
    local_path = args.local_path
    log_path = Path(args.log_path)
    groups = args.groups

    setup_logger(log_path)

    for group in groups:
        await sync_baselines(ftp_path, local_path, group)
        await sync_incrs(ftp_path, local_path, group)


if __name__ == "__main__":
    asyncio.run(main())

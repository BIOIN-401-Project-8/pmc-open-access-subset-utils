import argparse
import glob
import subprocess
from pathlib import Path

from tqdm import tqdm


def untar(tarball):
    subprocess.run(["tar", "-xzf", tarball], cwd="../data/ftp.ncbi.nlm.nih.gov/pub/pmc/oa_bulk/oa_comm/xml/")


def main():
    parser = argparse.ArgumentParser(description="Untar PMC Open Access Subset tarballs")
    parser.add_argument("path", help="Path to data directory")
    args = parser.parse_args()
    path = Path(args.path)

    baseline_tarballs = glob.glob(
        str(path / "ftp.ncbi.nlm.nih.gov/pub/pmc/oa_bulk/oa_comm/xml/oa_comm_xml.PMC***xxxxxx.baseline.*.tar.gz")
    )
    daily_update_tarballs = glob.glob(
        str(path / "ftp.ncbi.nlm.nih.gov/pub/pmc/oa_bulk/oa_comm/xml/oa_comm_xml.incr.*.tar.gz")
    )
    print(f"Found {len(baseline_tarballs)} baseline tarballs")
    print(f"Found {len(daily_update_tarballs)} daily update tarballs")
    for tarball in tqdm(baseline_tarballs):
        untar(tarball)

    daily_update_tarballs = list(sorted(daily_update_tarballs))

    for tarball in tqdm(daily_update_tarballs):
        untar(Path(tarball).absolute())
        Path(tarball).unlink()


if __name__ == "__main__":
    main()

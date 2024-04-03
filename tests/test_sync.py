import glob

import pytest

from src.sync import get_local_dates, get_remote_dates, main

pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_sync(tmp_path):
    await main(["--local_path", str(tmp_path), "--groups", "other"])
    paths = glob.glob(str(tmp_path) + "/oa_other/xml/*")
    paths = [path.removeprefix(str(tmp_path)) for path in paths]
    for i in range(1, 11):
        assert f"/oa_other/xml/PMC0{i:02}xxxxxx" in paths
    baseline_paths = [path for path in paths if "baseline" in path]
    assert len(baseline_paths) >= 11
    remote_dates = get_remote_dates("other")
    local_dates = get_local_dates(str(tmp_path), "other")
    dates_delta = sorted(set(remote_dates) - set(local_dates))
    assert not dates_delta

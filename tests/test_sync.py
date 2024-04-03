import pytest

from src.sync import main

pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_sync(tmp_path):
    await main(["--local_path", str(tmp_path), "--groups", "other"])
    assert tmp_path.exists()

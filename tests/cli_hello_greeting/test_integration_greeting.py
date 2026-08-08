from pathlib import Path
import subprocess
import sys


ROOT_DIR = Path(__file__).resolve().parents[2]
ENTRYPOINT = ROOT_DIR / "src" / "cli_hello_greeting" / "entrypoint.py"


def run_entrypoint(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(ENTRYPOINT), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )


def test_entrypoint_prints_greeting_for_alice():
    result = run_entrypoint("--name", "Alice")

    assert result.returncode == 0
    assert result.stdout == "Hello, Alice!\n"


def test_entrypoint_prints_greeting_for_japanese_name():
    result = run_entrypoint("--name", "太郎")

    assert result.returncode == 0
    assert result.stdout == "Hello, 太郎!\n"


def test_entrypoint_returns_non_zero_when_name_is_missing():
    result = run_entrypoint()

    assert result.returncode != 0

import sys
from pathlib import Path

# Add src to path
src_path = str(Path(__file__).resolve().parent.parent.parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

import pytest

# Try to import the module
try:
    from cli_text_masker.features.ascii_digit_masker import mask_ascii_digits
except ImportError as e:
    # Fallback: try relative import
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "ascii_digit_masker",
        Path(__file__).resolve().parent.parent.parent.parent / "src" / "cli_text_masker" / "features" / "ascii_digit_masker.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    mask_ascii_digits = module.mask_ascii_digits


class TestMaskAsciiDigits:
    """ASCII 数字マスカーのテスト"""

    def test_mixed_alphanumeric(self):
        """TV-001: 英数字混在で ASCII 数字だけが置換される"""
        assert mask_ascii_digits("A1B23") == "A*B**"

    def test_digits_only(self):
        """TV-002: ASCII 数字のみの文字列で全て置換される"""
        assert mask_ascii_digits("0123456789") == "**********"

    def test_no_digits(self):
        """TV-003: ASCII 数字を含まない文字列は不変"""
        assert mask_ascii_digits("ABCxyz!@#") == "ABCxyz!@#"

    def test_empty_string(self):
        """TV-004: 空文字列は空文字列を返す"""
        assert mask_ascii_digits("") == ""

    def test_unicode_digits_not_masked(self):
        """TV-005: 全角数字や Unicode 数字は置換対象にならない"""
        assert mask_ascii_digits("１23Ａ") == "１**Ａ"

    def test_return_type_and_no_stdout(self, capsys):
        """TV-006: 戻り値の型が str であり、標準出力を行わない"""
        result = mask_ascii_digits("test123")
        assert isinstance(result, str)
        assert result == "test***"

        captured = capsys.readouterr()
        assert captured.out == ""
        assert captured.err == ""

def mask_ascii_digits(text: str) -> str:
    """
    入力文字列中の ASCII 数字 (0-9) を '*' に置換し、その他の文字は保持する。

    Args:
        text: 変換対象の文字列

    Returns:
        ASCII 数字が '*' に置換された文字列
    """
    result = []
    for char in text:
        if '0' <= char <= '9':
            result.append('*')
        else:
            result.append(char)
    return ''.join(result)

from xml.etree import ElementTree as ET


def get_esearch_count(path: str) -> int:
    try:
        tree = ET.parse(path)
    except ET.ParseError:
        return 0
    count = tree.find('Count').text
    return int(count) if count else 0

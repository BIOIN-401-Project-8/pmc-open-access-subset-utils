from xml.etree import ElementTree as ET


def get_esearch_key(esearch_result: str, key: str = "Count") -> int:
    try:
        tree = ET.fromstring(esearch_result)
    except ET.ParseError:
        return 0
    count = tree.find(key).text
    return int(count) if count else 0

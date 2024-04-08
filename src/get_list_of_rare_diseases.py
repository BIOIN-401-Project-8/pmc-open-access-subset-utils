import xml.etree.ElementTree as ET

import pandas as pd


def main():
    rare_diseases = []

    # https://www.orphadata.com/data/xml/en_product7.xml
    with open("data/en_product7.xml", "r", encoding="ISO-8859-1") as f:
        root = ET.parse(f).getroot()
        for disorder in root.findall(".//Disorder"):
            name = disorder.find("Name").text
            rare_diseases.append(name)

    df = pd.DataFrame(rare_diseases, columns=["rare_disease"])
    df = df.drop_duplicates()
    df.to_csv("data/rare_diseases2.csv", index=False)


if __name__ == "__main__":
    main()

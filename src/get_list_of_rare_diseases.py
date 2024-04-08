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
    # for terms containing OR, we need to wrap them in parentheses
    df["rare_disease"] = df["rare_disease"].str.replace(r"([\w-]+ or [\w]+)", r"(\1)", regex=True)
    df.to_csv("data/rare_diseases.csv", index=False)


if __name__ == "__main__":
    main()

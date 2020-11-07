import xml.etree.ElementTree as ET
from beautifultable import BeautifulTable


def print_table(input_file):
    tree = ET.parse(input_file)
    print("printing for file: ", input_file)
    for element in tree.findall("element"):
        table = BeautifulTable(maxwidth=500)
        print("Printing for table name: ", element.find("meta").find("name").text)
        headers = []
        for column in element.find("sql").findall("columnDefinition"):
            name = column.find("meta").find("name").text
            type = column.find("columnTypeName").text
            headers.append(f"{name} ({type})")

        table.columns.header = headers

        for row in element.find("entries").findall("row"):
            temp = {}
            for col in row.findall("column"):
                key = col.find("name").text
                value = col.find("content").text
                temp[key] = value

            row_val = [temp[key.split(" ")[0]] for key in headers]
            table.rows.append(row_val)

        print(table)


input_files = [
    "Test/Q2/0A/0A-01.xml",
    "Test/Q2/0A/0A-02.xml",
    "Test/Q2/0A/0A-03.xml",
    "Test/Q2/0A/0A-04.xml",
    "Test/Q2/0A/0A-05.xml",
]

for input_file in input_files:
    print_table(input_file)

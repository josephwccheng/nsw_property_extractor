import csv


def createEmptyCsvWithHeaders(fileName: str, keyList: list):
    with open(fileName, 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keyList)
        dict_writer.writeheader()


def appendRowsToCsv(fileName: str, keyList: list, rows: list):
    with open(fileName, 'a', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keyList)
        dict_writer.writerows(rows)

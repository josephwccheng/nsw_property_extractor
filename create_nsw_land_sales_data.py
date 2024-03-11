import pandas as pd
from typing import List
import glob
import os
from tqdm import tqdm


NSW_LAND_VALUE_FILE_PATH = "./data/NSW_Land_Sales_Data"
OUTPUT_LAND_VALUE_FILE_PATH = "./output/nsw_land_sales_data.csv"
CSV_FORMAT = "*.csv"


def land_value_file_searcher(root_dir: str, file_format: str) -> List:
    property_metadata_list = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for dirname in dirnames:
            subdir_path = os.path.join(dirpath, dirname)
            ''' This is dependant on the file having the right folder name of numbers based on year
            data saved in data/NSW_Land_Sales_Data/LV_<yyyyMMdd>/ 
            Therefore we take the 4th element when splitting
            '''
            subdir_dat_files = glob.glob(
                os.path.join(subdir_path, file_format))
            property_metadata_list.extend(subdir_dat_files)
    if len(dirnames) == 0 and filenames:
        property_metadata_list = [
            f'{dirpath}/{filename}' for filename in filenames if ".csv" in filename]
    return property_metadata_list


def concatAddress(row: pd.Series):
    return f'{str(row["UNIT NUMBER"]) + "/" if not pd.isnull(row["UNIT NUMBER"]) else ""}{row["HOUSE NUMBER"] if not pd.isnull(row["HOUSE NUMBER"]) else ""} {row["STREET NAME"]}, {row["SUBURB NAME"]}'


def mergeAllLandValue(row: pd.Series):
    maxRecord = 5
    result = {}
    for i in range(1, maxRecord + 1):
        landValueColumn = f'LAND VALUE {i}'
        if landValueColumn in row and not pd.isnull(row[f'LAND VALUE {i}']):
            result[row[f'BASE DATE {i}'].split(
                '/')[2]] = row[f'LAND VALUE {i}']
    return result


def processMergedRows(row: pd.Series):
    columns = ["PROPERTY DESCRIPTION", "ADDRESS", "POSTCODE",
               "DISTRICT NAME", "DISTRICT CODE", "LAND VALUE"]
    for column in columns:
        if column == "LAND VALUE":
            if not pd.isnull(row["LAND VALUE_y"]) and not pd.isnull(row["LAND VALUE_x"]):
                row["LAND VALUE_x"].update(row["LAND VALUE_y"])
            elif not pd.isnull(row["LAND VALUE_y"]) and pd.isnull(row["LAND VALUE_x"]):
                row["LAND VALUE_x"] = row["LAND VALUE_y"]
        else:
            if pd.isnull(row[f'{column}_x']) and not pd.isnull(row[f'{column}_y']):
                row[f'{column}_x'] = row[f'{column}_y']
    return row


if __name__ == "__main__":
    LVFiles = ["LV_20240301", "LV_20190801", "LV_20170701"]
    dtype = {
        "DISTRICT CODE": "string",
        "DISTRICT NAME": "string",
        "PROPERTY ID": "string",
        "PROPERTY TYPE": "string",
        "PROPERTY NAME": "string",
        "UNIT NUMBER": "string",
        "HOUSE NUMBER": "string",
        "STREET NAME": "string",
        "SUBURB NAME": "string",
        "POSTCODE": "string",
        "PROPERTY DESCRIPTION": "string",
        "ZONE CODE": "string",
        "AREA": "string",
        "AREA TYPE": "string",
        "BASE DATE 1": "string",
        "LAND VALUE 1": "string",
        "AUTHORITY 1": "string",
        "BASIS 1": "string",
        "BASE DATE 2": "string",
        "LAND VALUE 2": "string",
        "AUTHORITY 2": "string",
        "BASIS 2": "string",
        "BASE DATE 3": "string",
        "LAND VALUE 3": "string",
        "AUTHORITY 3": "string",
        "BASIS 3": "string",
        "BASE DATE 4": "string",
        "LAND VALUE 4": "string",
        "AUTHORITY 4": "string",
        "BASIS 4": "string",
        "BASE DATE 5": "string",
        "LAND VALUE 5": "string",
        "AUTHORITY 5": "string",
        "BASIS 5": "string"
    }  # type: ignore
    for LVFile in tqdm(LVFiles):
        landValueList = []
        fileList = land_value_file_searcher(
            f'{NSW_LAND_VALUE_FILE_PATH}/{LVFile}', CSV_FORMAT)
        for file in tqdm(fileList):
            landValue_df = pd.read_csv(file, encoding='cp1252', dtype=dtype)
            address_df = landValue_df.apply(concatAddress, axis=1)
            mergedLandValue_df = landValue_df.apply(mergeAllLandValue, axis=1)
            landValue_df["ADDRESS"] = address_df
            landValue_df["LAND VALUE"] = mergedLandValue_df
            filteredLandSales_df = landValue_df[["PROPERTY ID", "PROPERTY DESCRIPTION",
                                                "ADDRESS", "POSTCODE", "DISTRICT NAME", "DISTRICT CODE", "LAND VALUE"]]
            landValueList.append(filteredLandSales_df)
        LVCombinedFile = pd.concat(landValueList)
        LVCombinedFile.to_csv(f'./output/{LVFile}.csv', index=False)
    # fileList = land_value_file_searcher(NSW_LAND_VALUE_FILE_PATH, CSV_FORMAT)
    # outputSchema = {
    #     "propertyId": 'string',
    #     "propertyDesc": 'string',
    #     "districtName": 'string',
    #     "address": "string",
    #     "suburb": "string",
    #     "propertyName": 'string',
    #     "landValues": 'dict'
    # }

    # output_df = pd.DataFrame()
    # for file in tqdm(fileList):
    #     landSales_df = pd.read_csv(file, encoding='cp1252')
    #     address_df = landSales_df.apply(concatAddress, axis=1)
    #     landValue_df = landSales_df.apply(mergeAllLandValue, axis=1)
    #     landSales_df["ADDRESS"] = address_df
    #     landSales_df["LAND VALUE"] = landValue_df
    #     filteredLandSales_df = landSales_df[["PROPERTY ID", "PROPERTY DESCRIPTION",
    #                                          "ADDRESS", "POSTCODE", "DISTRICT NAME", "DISTRICT CODE", "LAND VALUE"]]
    #     if output_df.empty:
    #         output_df = filteredLandSales_df
    #     else:
    #         output_df = pd.merge(
    #             output_df, filteredLandSales_df, on="PROPERTY ID", how="outer")
    #         output_df = output_df.apply(processMergedRows, axis=1)
    #         output_df = output_df.rename(columns={"PROPERTY DESCRIPTION_x": "PROPERTY DESCRIPTION", "ADDRESS_x": "ADDRESS", "POSTCODE_x": "POSTCODE",
    #                                               "DISTRICT NAME_x": "DISTRICT NAME", "DISTRICT CODE_x": "DISTRICT CODE", "LAND VALUE_x": "LAND VALUE"})
    #         output_df = output_df[["PROPERTY ID", "PROPERTY DESCRIPTION", "ADDRESS",
    #                                "POSTCODE", "DISTRICT NAME", "DISTRICT CODE", "LAND VALUE"]]
    # output_df.to_csv(OUTPUT_LAND_VALUE_FILE_PATH)
    print("done")

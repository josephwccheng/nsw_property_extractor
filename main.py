import glob
from current_nswvaluegeneral_type import RecordHeader, RecordAddrSales, RecordDesc, RecordOwner, RecordTrailer, NSWPropertyInfo, Property_Data_Type
from archived_nswvaluegeneral_type import Archived_RecordHeader, Archived_RecordAddrSales, Archived_NSWPropertyInfo, Archived_Property_Data_Type
from typing import List
import multiprocessing as mp
from multiprocessing import Queue
import csv
from datetime import datetime
import os
from dataclasses import dataclass

from tqdm import tqdm

# global variables
NSW_PROPERTY_DATA_OUTPUT = "nsw_property_data.csv"
NSW_PROPERTY_ARCHIVED_DATA_OUTPUT = "nsw_property_archived_data.csv"
NSW_DISTRICT_CODE_TO_COUNCIL = "nsw_district_code.csv"
NSW_VALUE_GENERAL_FILE_PATH = "./data/nsw/valuegeneral/"
DAT_FORMAT = "*.DAT"

district_code_mapping = {}
with open(NSW_DISTRICT_CODE_TO_COUNCIL, "r") as f:
    reader = csv.reader(f)
    district_code_mapping = {rows[0]:rows[1] for rows in reader}

def read_archived_nswvalue_dat_file(filename: str):
    with open(filename, "r") as file:
        data = file.readlines()
    data_split = [i.strip(";\n").split(";") for i in data]
    propertyList: List[Archived_NSWPropertyInfo] = []
    propertyHeader, propertyAddrSales = None, None
    for data in data_split:
        record_type = data[0]
        match record_type:
            case "A":
                propertyHeader = Archived_RecordHeader(data)
            case "B":
                # When record is B, if the record is new reset everything
                if propertyHeader and propertyAddrSales:
                    propertyList.append(Archived_NSWPropertyInfo(propertyHeader,propertyAddrSales))
                    propertyAddrSales = None
                else:
                    propertyAddrSales = Archived_RecordAddrSales(data)
    # Result is Filtered from the Raw Data
    archivedResults = []
    for rawResult in propertyList:
        header = rawResult.Header.get_record()
        addressSales = rawResult.AddressSales.get_record()
        archivedData = Archived_Property_Data_Type(
            property_id = addressSales.property_id,
            download_date = datetime.strptime(header.download_date, "%Y%m%d %H:%M").isoformat().split("T")[0],
            council_name = district_code_mapping[addressSales.district_code] if addressSales.district_code in list(district_code_mapping.keys()) else addressSales.district_code,
            contract_date = datetime.strptime(addressSales.contract_date,"%d/%m/%Y").isoformat().split("T")[0],
            purchase_price = addressSales.purchase_price,
            address = f'{addressSales.property_unit_number + "/" + addressSales.property_house_number if addressSales.property_unit_number != "" else addressSales.property_house_number} {addressSales.property_street_name}, {addressSales.property_suburb_name}',
            post_code = addressSales.property_post_code,
            property_type = "unit" if addressSales.property_unit_number != "" else "house",
            area =  addressSales.area,
            area_type = addressSales.area_type,
            land_description = addressSales.land_description
        )
        archivedResults.append(archivedData.__dict__)
    return { "data": archivedResults, "version": "archived"}

def read_nswvalue_dat_file(filename: str):
    with open(filename, "r") as file:
        data = file.readlines()
    data_split = [i.strip(";\n").split(";") for i in data]
    propertyList: List[NSWPropertyInfo] = []
    propertyHeader, propertyAddrSales, propertyDesc, propertyOwner = None, None, None, []
    for data in data_split:
        record_type = data[0]
        match record_type:
            case "A":
                propertyHeader = RecordHeader(data)
            case "B":
                # When record is B, if the record is new reset everything
                if propertyHeader and propertyAddrSales and propertyDesc and propertyOwner:
                    propertyList.append(NSWPropertyInfo(propertyHeader,propertyAddrSales,propertyDesc,propertyOwner))
                    propertyAddrSales, propertyDesc, propertyOwner = None, None, []
                else:
                    propertyAddrSales = RecordAddrSales(data)
            case "C":
                propertyDesc = RecordDesc(data)
            case "D":
                propertyOwner.append(RecordOwner(data))
            # case "Z":
            #     print("(TODO) - Not implemented")
                # fileTrailer = RecordTrailer(data)
    # Result is Filtered from the Raw Data
    results = []
    for rawResult in propertyList:
        header = rawResult.Header.get_record()
        addressSales = rawResult.AddressSales.get_record()
        description = rawResult.Description.get_record()
        # owners = rawResult.Owner
        data = Property_Data_Type(
            property_id = addressSales.property_id,
            download_date = datetime.strptime(addressSales.download_date, "%Y%m%d %H:%M").isoformat().split("T")[0],
            council_name = district_code_mapping[addressSales.district_code] if addressSales.district_code in list(district_code_mapping.keys()) else addressSales.district_code,
            contract_date = datetime.strptime(addressSales.contract_date,"%Y%m%d").isoformat().split("T")[0] if addressSales.contract_date != "" else addressSales.contract_date,
            purchase_price = addressSales.purchase_price,
            address = f'{addressSales.property_unit_number + "/" + addressSales.property_house_number if addressSales.property_unit_number != "" else addressSales.property_house_number} {addressSales.property_street_name}, {addressSales.property_locality}',
            post_code = addressSales.property_post_code,
            property_type = "unit" if addressSales.property_unit_number != "" else "house",
            strata_lot_number = addressSales.strata_lot_number,
            property_name = addressSales.property_name,
            area = addressSales.area,
            area_type = addressSales.area_type,
            settlement_date = datetime.strptime(addressSales.settlement_date,"%Y%m%d").isoformat().split("T")[0] if addressSales.settlement_date != "" else addressSales.settlement_date,
            nature_of_property = addressSales.nature_of_property,
            primary_purpose = addressSales.primary_purpose,
            legal_description = description.property_legal_desc
        )
        results.append(data.__dict__)
    return { "data": results, "version": "current"}

def worker_function(results, queue: Queue):
    queue.put(results)

def listener(queue: Queue):
    """
    continue to listen for messages on the queue and writes to file when receive one
    if it receives a '#done#' message it will exit
    """
    with open(NSW_PROPERTY_DATA_OUTPUT, 'a+') as f_current, open(NSW_PROPERTY_ARCHIVED_DATA_OUTPUT, 'a+') as f_archived:
        while True:
            m = queue.get()
            if m['version'] == 'current':
                current_header = list(Property_Data_Type.__dataclass_fields__)
                writer_current= csv.DictWriter(f_current, fieldnames= current_header)
                writer_current.writerows(m['data'])
            elif m['version'] == 'archived':
                archived_header = list(Archived_Property_Data_Type.__dataclass_fields__)
                writer_archived= csv.DictWriter(f_archived, fieldnames = archived_header)
                writer_archived.writerows(m['data'])
            elif m == 'done':
                break

@dataclass
class propertyMetadata:
    year:int
    filePath:str

def file_searcher(root_dir:str, file_format: str) -> List[propertyMetadata]:
    property_metadata_list = []    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for dirname in dirnames:
            subdir_path = os.path.join(dirpath, dirname)
            # This is dependant on the file having the right folder name of numbers based on year
            year = int(subdir_path.split('/')[4][0:4])
            subdir_dat_files = glob.glob(os.path.join(subdir_path, file_format))
            subdir_property_metadata_list = [propertyMetadata(year, subdir_file) for subdir_file in subdir_dat_files]
            property_metadata_list.extend(subdir_property_metadata_list)
    return property_metadata_list

if __name__ == "__main__":

    # 1. check output file, if they exist delete them
    with open(NSW_PROPERTY_DATA_OUTPUT, 'w') as f_current, open(NSW_PROPERTY_ARCHIVED_DATA_OUTPUT, 'w') as f_archived:
        current_header = list(Property_Data_Type.__dataclass_fields__)
        writer_current= csv.DictWriter(f_current, fieldnames= current_header)
        writer_current.writeheader()

        archived_header = list(Archived_Property_Data_Type.__dataclass_fields__)
        writer_archived= csv.DictWriter(f_archived, fieldnames = archived_header)
        writer_archived.writeheader()
    
    # 2. Multiprocessing Part
    # Archecture - having multiple worker nodes extract data from dat files
    # Create a queue and use one worker to update the results into one single file
    manager = mp.Manager()
    queue = manager.Queue()
    file_pool = mp.Pool(1)
    file_pool.apply_async(listener, (queue, ))

    pool = mp.Pool(16)
    jobs = []

    # 2.1. identify all the folders in the data file path
    property_metadata_list = file_searcher(NSW_VALUE_GENERAL_FILE_PATH, DAT_FORMAT)
    for property_metadata in tqdm(property_metadata_list, desc= f'processing folders'):   
        if property_metadata.year > 2000:
            job = pool.apply_async(worker_function, (read_nswvalue_dat_file(property_metadata.filePath), queue))
        else:
            job = pool.apply_async(worker_function, (read_archived_nswvalue_dat_file(property_metadata.filePath), queue))
        jobs.append(job)
    
    for job in jobs:
        job.get()
    
    queue.put('done') # all workers are done, we close the output file
    pool.close()
    pool.join()
    print("completed extracted files")



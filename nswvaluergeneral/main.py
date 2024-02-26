import glob
from current_nswvaluegeneral import Property_Data_Type, read_nswvalue_dat_file
from archived_nswvaluegeneral import Archived_Property_Data_Type, read_archived_nswvalue_dat_file
from typing import List
import multiprocessing as mp
from multiprocessing import Queue
import csv
import os
from dataclasses import dataclass
from tqdm import tqdm

# global variables
NSW_PROPERTY_DATA_OUTPUT = "nsw_property_data.csv"
NSW_PROPERTY_ARCHIVED_DATA_OUTPUT = "nsw_property_archived_data.csv"
NSW_DISTRICT_CODE_TO_COUNCIL = "nsw_district_code.csv"
NSW_VALUE_GENERAL_FILE_PATH = "./data/nsw/valuegeneral/"
DAT_FORMAT = "*.DAT"


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
                writer_current = csv.DictWriter(
                    f_current, fieldnames=current_header)
                writer_current.writerows(m['data'])
            elif m['version'] == 'archived':
                archived_header = list(
                    Archived_Property_Data_Type.__dataclass_fields__)
                writer_archived = csv.DictWriter(
                    f_archived, fieldnames=archived_header)
                writer_archived.writerows(m['data'])
            elif m == 'done':
                break


@dataclass
class propertyFileMetadata:
    year: int
    filePath: str


def property_file_searcher(root_dir: str, file_format: str) -> List[propertyFileMetadata]:
    property_metadata_list = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for dirname in dirnames:
            subdir_path = os.path.join(dirpath, dirname)
            ''' This is dependant on the file having the right folder name of numbers based on year
            data saved in data/nsw/valuegeneral/<xxyearxx>/ 
            Therefore we take the 4th element when splitting
            '''
            year = int(subdir_path.split('/')[4][0:4])
            subdir_dat_files = glob.glob(
                os.path.join(subdir_path, file_format))
            subdir_property_metadata_list = [propertyFileMetadata(
                year, subdir_file) for subdir_file in subdir_dat_files]
            property_metadata_list.extend(subdir_property_metadata_list)
    return property_metadata_list


if __name__ == "__main__":

    # 1. check output file, if they exist delete them
    with open(NSW_PROPERTY_DATA_OUTPUT, 'w') as f_current, open(NSW_PROPERTY_ARCHIVED_DATA_OUTPUT, 'w') as f_archived:
        current_header = list(Property_Data_Type.__dataclass_fields__)
        writer_current = csv.DictWriter(f_current, fieldnames=current_header)
        writer_current.writeheader()

        archived_header = list(
            Archived_Property_Data_Type.__dataclass_fields__)
        writer_archived = csv.DictWriter(
            f_archived, fieldnames=archived_header)
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
    property_metadata_list = property_file_searcher(
        NSW_VALUE_GENERAL_FILE_PATH, DAT_FORMAT)
    for property_metadata in tqdm(property_metadata_list, desc=f'processing folders'):
        if property_metadata.year > 2000:
            job = pool.apply_async(
                worker_function, (read_nswvalue_dat_file(property_metadata.filePath), queue))
        else:
            job = pool.apply_async(worker_function, (read_archived_nswvalue_dat_file(
                property_metadata.filePath), queue))
        jobs.append(job)

    for job in jobs:
        job.get()

    queue.put('done')  # all workers are done, we close the output file
    pool.close()
    pool.join()
    print("completed extracted files")

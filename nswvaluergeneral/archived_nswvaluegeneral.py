# documentation schema located
# https://www.valuergeneral.nsw.gov.au/__data/assets/pdf_file/0016/216403/Property_Sales_Data_File_-_Data_Elements_V3.pdf

from typing import List
from datetime import datetime
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
import warnings
import csv

NSW_DISTRICT_CODE_TO_COUNCIL = "nsw_district_code.csv"
district_code_mapping = {}
with open(NSW_DISTRICT_CODE_TO_COUNCIL, "r") as f:
    reader = csv.reader(f)
    district_code_mapping = {rows[0]: rows[1] for rows in reader}


@dataclass
class Archived_A:
    district_code: str
    download_date: str
    submitter_user_id: str


@dataclass
class Archived_B:
    district_code: str
    source: str  # internal use only
    valuation_num: str
    property_id: str
    property_unit_number: str
    property_house_number: str
    property_street_name: str
    property_suburb_name: str
    property_post_code: str
    contract_date: str
    purchase_price: float
    land_description: str
    area: float
    area_type: str
    dimensions: str
    comp_code: str
    zone_code: str
    # vendor_name: str
    # purchaser_name: str


@dataclass
class Archived_Property_Data_Type:
    property_id: str
    download_date: str
    council_name: str
    purchase_price: float
    address: str
    post_code: str
    property_type: str
    area: float
    area_type: str
    contract_date: str
    land_description: str


@dataclass
class Archived_Z:
    total_records: str  # Include A and Z records
    total_B_record: str


class Extractor(ABC):
    @abstractmethod
    def check_len_args(self) -> bool:
        pass

    @abstractmethod
    def set_record_from_args(self) -> bool:
        pass

    @abstractmethod
    def get_record(self):
        pass


class Archived_RecordHeader(Extractor):
    def __init__(self, args) -> None:
        self.length_args = 4
        self.len_check: bool = self.check_len_args(args)
        self.record = self.set_record_from_args(args)

    def check_len_args(self, args):
        if (len(args) != self.length_args):
            warnings.warn(
                "lenght of argument is not correct for Record Header")
            return False
        return True

    def set_record_from_args(self, args):
        if not self.len_check:
            args.extend([""]*(self.length_args - len(args)))
        return Archived_A(
            district_code=args[1],
            submitter_user_id=args[2],
            download_date=args[3],

        )

    def get_record(self):
        return self.record


class Archived_RecordAddrSales(Extractor):
    def __init__(self, args) -> None:
        self.length_args = 18
        self.len_check: bool = self.check_len_args(args)
        self.record = self.set_record_from_args(args)

    def check_len_args(self, args):
        if (len(args) < self.length_args):
            warnings.warn(
                f"lenght of argument is not correct for Record Address Sales")
            return False
        return True

    def set_record_from_args(self, args):
        if not self.len_check:
            args.extend([""]*(self.length_args - len(args)))
        return Archived_B(
            district_code=args[1],
            source=args[2],
            valuation_num=args[3],
            property_id=args[4],
            property_unit_number=args[5],
            property_house_number=args[6],
            property_street_name=args[7],
            property_suburb_name=args[8],
            property_post_code=args[9],
            contract_date=args[10],
            purchase_price=args[11],
            land_description=args[12],
            area=args[13],
            area_type=args[14],
            dimensions=args[15],
            comp_code=args[16],
            zone_code=args[17],
            # vendor_name = args[18],
            # purchaser_name = args[19],
        )

    def get_record(self):
        return self.record


class Archived_RecordTrailer(Extractor):
    def __init__(self, args) -> None:
        self.length_args = 2
        self.len_check: bool = self.check_len_args(args)
        self.record = self.set_record_from_args(args)

    def check_len_args(self, args):
        if (len(args) != 2):
            warnings.warn(
                "lenght of argument is not correct for Record Trailer")
            return False
        return True

    def set_record_from_args(self, args):
        if not self.len_check:
            args.extend([""]*(self.length_args - len(args)))
        return Archived_Z(
            total_records=args[1],  # Include A and Z records
            total_B_record=args[2],
        )

    def get_record(self):
        return self.record


@dataclass
class Archived_NSWPropertyInfo:
    Header: Archived_RecordHeader  # File Metadata
    AddressSales: Archived_RecordAddrSales  # Property Info


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
                    propertyList.append(Archived_NSWPropertyInfo(
                        propertyHeader, propertyAddrSales))
                    propertyAddrSales = None
                else:
                    propertyAddrSales = Archived_RecordAddrSales(data)
    # Result is Filtered from the Raw Data
    archivedResults = []
    for rawResult in propertyList:
        header = rawResult.Header.get_record()
        addressSales = rawResult.AddressSales.get_record()
        archivedData = Archived_Property_Data_Type(
            property_id=addressSales.property_id,
            download_date=datetime.strptime(
                header.download_date, "%Y%m%d %H:%M").isoformat().split("T")[0],
            council_name=district_code_mapping[addressSales.district_code] if addressSales.district_code in list(
                district_code_mapping.keys()) else addressSales.district_code,
            contract_date=datetime.strptime(
                addressSales.contract_date, "%d/%m/%Y").isoformat().split("T")[0],
            purchase_price=addressSales.purchase_price,
            address=f'{addressSales.property_unit_number + "/" + addressSales.property_house_number if addressSales.property_unit_number != "" else addressSales.property_house_number} {addressSales.property_street_name}, {addressSales.property_suburb_name}',
            post_code=addressSales.property_post_code,
            property_type="unit" if addressSales.property_unit_number != "" else "house",
            area=addressSales.area,
            area_type=addressSales.area_type,
            land_description=addressSales.land_description
        )
        archivedResults.append(archivedData.__dict__)
    return {"data": archivedResults, "version": "archived"}


if __name__ == '__main__':
    print("Typing for achvied nsw value general (from 1990 - 2000)")

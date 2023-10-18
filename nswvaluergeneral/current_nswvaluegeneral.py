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
    district_code_mapping = {rows[0]:rows[1] for rows in reader}

@dataclass
class A:
    file_type:str
    district_code:str
    download_date:str
    submitter_user_id:str

@dataclass
class B:
    district_code: str
    property_id: str
    sale_counter: str
    download_date: str
    property_name:str
    property_unit_number:str
    property_house_number:str
    property_street_name:str        
    property_locality:str
    property_post_code:str
    area:float
    area_type:str
    contract_date:str
    settlement_date:str
    purchase_price:float
    zoning:str
    nature_of_property:str
    primary_purpose:str
    strata_lot_number:str
    component_code:str
    sale_code:str
    interest_of_sale:str
    dealing_number:str

@dataclass
class C:
    district_code: str
    property_id: str
    sale_counter: str
    download_date: str
    property_legal_desc: str

@dataclass
class D:
    district_code: str
    property_id: str
    sale_counter: str
    download_date: str
    purchaser_vendor: str

@dataclass
class Z:
    total_record: str #Include A and Z records
    total_B_record: str
    total_C_record: str
    total_D_record: str

@dataclass
class Property_Data_Type:
    property_id: str
    download_date: str
    council_name: str
    purchase_price: float
    address: str
    post_code: str
    property_type:str
    strata_lot_number: str
    property_name: str
    area: float
    area_type: str
    contract_date: str
    settlement_date: str
    nature_of_property: str
    primary_purpose: str
    legal_description: str

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

class RecordHeader(Extractor):
    def __init__(self, args) -> None:
        self.length_args = 5
        self.len_check: bool = self.check_len_args(args)
        self.record = self.set_record_from_args(args)

    def check_len_args(self, args):
        if (len(args) < self.length_args):
            warnings.warn("lenght of argument is not correct for Record Header")
            return False
        return True
    
    def set_record_from_args(self, args):
        if not self.len_check:
            return A(
                file_type = "", 
                district_code = args[1],
                download_date = args[2],
                submitter_user_id = args[3],
            )
        return A(
            file_type = args[1],
            district_code = args[2],
            download_date = args[3],
            submitter_user_id = args[4],
        )

    def get_record(self):
        return self.record
    
class RecordAddrSales(Extractor):
    def __init__(self, args) -> None:
        self.length_args = 24
        self.len_check: bool = self.check_len_args(args)
        self.record = self.set_record_from_args(args)

    def check_len_args(self, args):
        if (len(args) != self.length_args):
            warnings.warn("lenght of argument is not correct for Record Address Sales")
            return False
        return True
    
    def set_record_from_args(self, args):
        if not self.len_check:
            args.extend([""]*(self.length_args - len(args)))
        return B(
            district_code = args[1],
            property_id = args[2],
            sale_counter = args[3],
            download_date = args[4],
            property_name = args[5],
            property_unit_number = args[6],
            property_house_number = args[7],
            property_street_name = args[8],        
            property_locality = args[9],
            property_post_code = args[10],
            area = args[11],
            area_type = args[12],
            contract_date = args[13],
            settlement_date = args[14],
            purchase_price = args[15],
            zoning = args[16],
            nature_of_property = args[17],
            primary_purpose = args[18],
            strata_lot_number = args[19],
            component_code = args[20],
            sale_code = args[21],
            interest_of_sale = args[22],
            dealing_number = args[23]
        )

    def get_record(self):
        return self.record

class RecordDesc(Extractor):
    def __init__(self, args) -> None:
        self.length_args = 6
        self.len_check: bool = self.check_len_args(args)
        self.record = self.set_record_from_args(args)

    def check_len_args(self, args):
        if (len(args) < self.length_args):
            warnings.warn("lenght of argument is not correct for Record Description")
            return False
        return True
    
    def set_record_from_args(self, args):
        if not self.len_check:
            args.extend([""]*(self.length_args - len(args)))
        return C(
            district_code = args[1],
            property_id= args[2],
            sale_counter= args[3],
            download_date= args[4],
            property_legal_desc= args[5]
        )

    def get_record(self):
        return self.record

class RecordOwner(Extractor):
    def __init__(self, args) -> None:
        self.length_args = 6
        self.len_check: bool = self.check_len_args(args)
        self.record = self.set_record_from_args(args)

    def check_len_args(self, args):
        if (len(args) != self.length_args):
            warnings.warn("lenght of argument is not correct for Record Owner")
            return False
        return True
    
    def set_record_from_args(self, args):
        if not self.len_check:
            args.extend([""]*(self.length_args - len(args)))
        return D(
            district_code= args[1],
            property_id= args[2],
            sale_counter= args[3],
            download_date= args[4],
            purchaser_vendor= args[5]
        )

    def get_record(self):
        return self.record

class RecordTrailer(Extractor):
    def __init__(self, args) -> None:
        self.length_args = 5
        self.len_check: bool = self.check_len_args(args)
        self.record = self.set_record_from_args(args)

    def check_len_args(self, args):
        if (len(args) != self.length_args):
            warnings.warn("lenght of argument is not correct for Record Trailer")
            return False
        return True
    
    def set_record_from_args(self, args):
        if not self.len_check:
            args.extend([""]*(self.length_args - len(args)))
        return Z(
            total_record = args[1], #Include A and Z records
            total_B_record = args[2],
            total_C_record = args[3],
            total_D_record = args[4]
        )

    def get_record(self):
        return self.record

@dataclass
class NSWPropertyInfo:
    Header: RecordHeader # File Metadata
    AddressSales: RecordAddrSales # Property Info
    Description: RecordDesc # Legal Description
    Owner: List[RecordOwner] # Purchase Vendor

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

if __name__ == '__main__':
    print("Typing for nsw value general (2001 onwards)")

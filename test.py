from nswPropertySales import currentNSWPropertySales

fileName = "./test/mock/002_SALES_DATA_NNME_08072019.DAT"
result = currentNSWPropertySales.read_nswvalue_dat_file(fileName)
print("done")

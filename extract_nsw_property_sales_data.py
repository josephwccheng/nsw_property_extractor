import pandas as pd


'''
After extracting the nsw_property_sales_data.csv file from "create_nsw_property_sales_data", this script is intented to perform some simple filtering
'''
nswPropData_df = pd.read_csv("output/nsw_property_sales_data.csv")

propertyId = 4047407
# selecting rows based on condition
result_df = nswPropData_df[nswPropData_df['property_id'] == propertyId]
result_df.to_csv(f'./output/{propertyId}.csv', index=False)
print("finish")

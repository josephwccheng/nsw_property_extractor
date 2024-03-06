import pandas as pd


nswPropData_df = pd.read_csv("output/nsw_property_data.csv")

propertyId = 4047407
# selecting rows based on condition
result_df = nswPropData_df[nswPropData_df['property_id'] == propertyId]
result_df.to_csv(f'{propertyId}.csv', index=False)
print("finish")

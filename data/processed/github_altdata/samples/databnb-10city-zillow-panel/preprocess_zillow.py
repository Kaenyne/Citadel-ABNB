import numpy as np
import pandas as pd
import sqlite3

# READING IN DATA FROM CSV FILES
def read_data(path):
	with open(path) as f:

		df = pd.read_csv(f)
	return df


# DATA PROCESSING
def process_zillow_data(df, cols_to_drop, locations):
	# Drop unnecessarily columns
	df.drop(df.columns[cols_to_drop], axis=1, inplace=True)
	# Drop cities we don't care about
	df = df[(df["City"] + df["State"]).isin(locations)]
	# Change data types
	df[['City', 'State']] = df[['City', 'State']].astype('str', copy=False)
	for c in df.columns[3:]:
	        df[c] = df[c].astype('float64', copy=False)
	# print(df.columns)
	# print(df.describe())
	# print(df.dtypes)
	# fixing column names to match the airbnb data
	df.columns = map(str.lower, df.columns)
	df = df.rename(columns={'regionname':'zipcode'})
	return df


# INSERTING TABLES INTO DATABASE
def add_to_db(df, path_to_db, table_name):
	conn = sqlite3.connect(path_to_db)
	# c = conn.cursor()
	df.to_sql(table_name, conn, if_exists="replace")
	conn.close()


def main():
	path_hv = "./data/zillow/Zip_Zhvi_AllHomes.csv"
	path_r = "./data/zillow/Zip_Zri_AllHomesPlusMultifamily.csv"
	path_to_db = './data/housing.db'
	locations = ["BostonMA", "ChicagoIL", "San FranciscoCA", "New YorkNY", "NashvilleTN", "Los AngelesCA", "AustinTX", "SeattleWA", "DenverCO", "AshevilleNC"]

	df_hv = read_data(path_hv)
	print("Finished reading data from {}".format(path_hv))
	df_r = read_data(path_r)
	print("Finished reading data from {}".format(path_r))

	'''
		Drop the following columns from df_hv
		0. Region ID
		4. Metro
		5. CoutryName
		6. SizeRank
		7. - 231. All data from months before 2015
	'''
	cols_to_drop_hv = [0] + list(range(4, 232))
	'''
		Drop the following columns
		0. Region ID
		4. Metro
		5. CoutryName
		6. SizeRank
		7. - 58. All data from months before 2015
	'''
	cols_to_drop_r = [0] + list(range(4, 59))

	df_hv = process_zillow_data(df_hv, cols_to_drop_hv, locations)
	print("Finished processing data from {}".format(path_hv))
	df_r = process_zillow_data(df_r, cols_to_drop_r, locations)
	print("Finished processing data from {}".format(path_r))

	add_to_db(df_hv, path_to_db, "zillow_zhvi")
	print("Finished adding to database from {}".format(path_hv))
	add_to_db(df_r, path_to_db, "zillow_zri")
	print("Finished adding to database from {}".format(path_r))


if __name__ == "__main__":
	main()
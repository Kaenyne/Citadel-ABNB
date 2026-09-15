import numpy as np
import pandas as pd
import sqlite3
import re
import requests
from io import StringIO
from os import listdir
from preprocess_zillow import add_to_db, read_data

# DATA PROCESSING
def process_airbnb_data(df, cols_to_keep, money_cols, filename):
    # Select certain columns from the downloaded CSV
    df = df[cols_to_keep]

    # Remove rows with no zipcodes
    df = df.dropna(subset = ['zipcode'])
    # Extracts zip codes using a regex
    df['zipcode'] = df['zipcode'].map(lambda x: re.findall('\\d{5}|$', x)[0] if isinstance(x, str) else x)
    df = df[df['zipcode'] != '']
    # Finally changes the type now that we've removed zip codes that can't be parsed into integers, like 12345-6789
    df['zipcode'] = df['zipcode'].astype(int, copy=False)

    # Create a column of consistent city names, drawn from the file names rather than the data itslef
    city = re.split('\\d|-', filename)[0]
    df.insert(1, 'cityname', city)

    # Now we convert any column in money_cols to FLOAT
    for col in money_cols:
        df[col] = df[col].str.replace('$', '').str.replace(',', '')
        df[col] = df[col].astype(float, copy=False)

    # We uppercase the state column to make it consistent
    df['state'] = df['state'].str.upper()

    return df

def main():
    local_csv_dir = './data/airbnb/'
    dropbox_link_file = './data/dropbox_links.txt'
    path_to_db = './data/housing.db'
    cols_to_keep = ['id', 'last_scraped', 'street', 'neighbourhood_cleansed', 'city', 'state', 'zipcode', 'latitude', 'longitude', 'accommodates', 'bathrooms', 'bedrooms', 'beds', 'price', 'weekly_price', 'monthly_price', 'security_deposit', 'cleaning_fee', 'minimum_nights', 'maximum_nights', 'calendar_updated', 'availability_30', 'availability_60', 'availability_90']
    money_cols = ['price', 'weekly_price', 'monthly_price', 'security_deposit', 'cleaning_fee']

    all_cities_df = pd.DataFrame()

    with open(dropbox_link_file) as f:
        dropbox_csv_links = f.read().splitlines()
        print(dropbox_csv_links)

    for url in dropbox_csv_links:
        filename = url.split('/')[-1].split('?')[0]

        df = pd.read_csv(url)
        print("Finished reading data from {}".format(filename))

        df = process_airbnb_data(df, cols_to_keep, money_cols, filename)
        print("Finished processing data from {}".format(filename))

        all_cities_df = all_cities_df.append(df)


    for filename in listdir(local_csv_dir):
        path = local_csv_dir + filename
        df = read_data(path)
        print("Finished reading data from {}".format(path))

        df = process_airbnb_data(df, cols_to_keep, money_cols, filename)
        print("Finished processing data from {}".format(path))

        all_cities_df = all_cities_df.append(df)

    add_to_db(all_cities_df, path_to_db, 'airbnb')
    print("Finished processing data from {}".format(path))




if __name__ == "__main__":
    main()
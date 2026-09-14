
# Data Analytics Project: NYC Airbnb 2024

## Overview

This project analyzes Airbnb listing data for New York City as of January 5, 2024. The dataset was obtained from [Kaggle.com](https://www.kaggle.com/datasets/vrindakallu/new-york-dataset). The primary objectives of this project are to organize the data, store it in an SQLite3 database, and create a Power BI dashboard for visual exploration.

## Project Structure

-   **/Airbnb PowerBi Dashboard.pdf**: Includes pdf snapshot of the dashboard created using PowerBi.
-   **/Airbnb Project Dashboard.pbix**: Includes interactive PowerBI dashboard file used to visualize data relating to the dataset.
-  **/database.db**: Stores the SQLite3 database file.
- **/project_summary.pdf**: The pdf summary of findings of the project.
-   **/new_york_listings_2024.csv**: Contains the raw CSV file downloaded from Kaggle.
-   **/sample_queries.sql**: Includes example queries that may be run on the database.db file.
-   **/schema.sql**: Contains all tables created to assist in data querying.


## Steps to Replicate

1.  **Download Data**: Obtain the dataset from [Kaggle.com](https://www.kaggle.com/datasets/vrindakallu/new-york-dataset) or download /new_york_listings_2024.csv.

2. **Create SQLite3 Database**: 
	- Ensure all relevant files are in the same directory.
	- Run the following commands in your Linux terminal: 
	```bash 
	sqlite3 database.db 
	.read schema.sql
	```
	- These commands open the SQLite3 shell, apply the database schema using the `schema.sql` file, import data from the CSV file into the SQLite3 database and populate tables derived from the primary table "all_listings".

4.  **Power BI Dashboard**:
    
    -   Open Power BI and connect to the SQLite3 database.
	- Follow these steps to connect Power BI to the SQLite3 database:
	    - Click on "Get Data" in "Home" section
	    - Select the "More" option,
	    - Choose "Other".
	    - Click "ODBC" and then select "Connect"
	    - Choose DSN (Data source name) "SQLite3 Datasource."
	    -  Click the drop-down for "Advanced Option"
	    - Enter "Database \(or whichever name you prefer) =" followed by the file path to the database file.
	    - Use your current credentials to authorize. 
    -   Load data and create visualizations using the tables and relationships defined in the database.

## Database Schema

-   ### `all_listings` Table

-   **Description:** Stores all data from the "new_york_listings_2024.csv" file.
-   **Columns:**
    -   `id`: Listing ID (Primary Key)
    -   `name`: Listing name
    -   `host_id`: Host ID
    -  `neighborhood_group`: Borough
    - `neighborhood`: Neighborhood within specific boroughs
    - `latitude`: Latitude of residence
    - `longitude`: Longitude of residence
    - `room_type`: Type of listing, "Entire house", "Private room", etc.
    - `price`: Price per night
    - `minimum_nights`: Minimum nights required for reservation
    - `number_of_reviews`: Number of reviews a listing has
    - `last_review`: Date the last reviews was left.
    - `reviews_per_month`: Average reviews per month a listing has recieved.
    - `calculated_host_listings_count`:  The amount of listings the host of the residence has.
    - `availability_365`: The amount of days per year the listing is available.
    - `number_of_reviews_ltm`: The number of reviews left last month.
    - `license`: The type of license the host has.
    - `rating`: The average rating a listing has received. (Values include: "No rating" and "New")
    - `bedrooms`: Number of bedrooms a at a listing.
    - `beds`: Number of beds (not always equal to the number of bedrooms) at a listing.
    - `baths`: Number of bathrooms at a listing.

### Borough Tables

-   **Description:** Separate tables for each borough (Brooklyn, Bronx, Manhattan, Queens, Staten Island).
-   **Columns:**
    -   Same as `all_listings` stratified by Borough for easier querying.

### `hosts` Table

-   **Description:** Analytical table for host-related insights.
-   **Columns:**
    -   `host_id`: Host ID (Primary Key)
    -   `host_name`: Host name
    -   `host_listings_count`: Count of listings by the host
    -   `host_total_reviews`: Total reviews received by the host

### `neighborhoods` Table

-   **Description:** Analytical table for neighborhood-related insights.
-   **Columns:**
    -   `neighborhood`: Neighborhood name (Primary Key)
    -   `average_price`: Average price of listings in the neighborhood
    -   `number_of_reviews`: Total number of reviews in the neighborhood

### `top_ten_listings` Table

-   **Description:** Lists the top ten listings based on the number of reviews.
-   **Columns:**
    -   `id`: Listing ID (Primary Key)
    -   `name`: Listing name
    -   `neighborhood_group`: Borough of the listing
    -   `number_of_reviews`: Total number of reviews
    -   `price`: Listing price

### `avg_neighborhood_price_manhattan` Table

-   **Description:** Provides average listing prices for neighborhoods in Manhattan.
-   **Columns:**
    -   `neighborhood`: Neighborhood name
    -   `avg_price`: Average price of listings in the neighborhood

### `filtered_ratings` Table

-   **Description:** A table with listings having ratings excluding "No rating" values.
-   **Columns:**
    -   Same as `all_listings`

### Filtered Borough Rating Tables

-   **Description:** Separate tables for listings in each borough with ratings excluding "No rating" values.
-   **Columns:**
    -   `id`: Listing ID (Primary Key)
    -   `name`: Listing name
    -   `host_id`: Host ID
    -   `neighborhood`: Neighborhood name
    -   `rating`: Listing rating

### Indexes

-   **Purpose:** Speeds up searches for listing names, prices, and ratings in each borough table.
-   **Indexes:**
    -   `brooklyn_listing_index`
    -   `bronx_listing_index`
    -   `manhattan_listing_index`
    -   `queens_listing_index`
    -   `staten_island_listing_index`

## Addendum
- Kaggle Collaboration including SQL and Python code [here](https://www.kaggle.com/code/traceycsneed/airbnb-2024-project#Python-EDA)


## Dependencies

- [SQLite3](https://www.sqlite.org/download.html): Download and install SQLite3 for managing the database.
- [Power BI](https://powerbi.microsoft.com/): Download and install Power BI for visualizing and exploring the data with the provided dashboard file.


## Acknowledgments

-   Kaggle for providing the dataset.
-   SQLite3 and Power BI communities for their valuable tools and resources.

## Contact

For any inquiries or suggestions, please contact Tracey Sneed at [traceysneed510@gmail.com](mailto:traceysneed510@gmail.com).

----------

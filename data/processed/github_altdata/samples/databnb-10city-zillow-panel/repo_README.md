Contributers: mdick, jmarkey, ykim117, akitatak

Our project looks at real estate market data in comparison with Airbnb data to address the question of: How does Airbnb impact the real estate market, or vice versa? We hypothesize that when the real estate market is successful in a particular neighborhood, the Airbnb market will also be successful. We think that there will be a positive correlation between the housing market and the Airbnb market because when neighborhoods are successfully building and selling houses, there is more possibility of people renting their houses on Airbnb.

This is a worthwhile question from the perspective of the Airbnb marketing team. Airbnb may want to market more aggressively in areas where houses are being sold and rented.

Additionally, with the Airbnb market growing, different stakeholders of real estate markets are expressing both positive and negative views towards Airbnb market. This calls for more government regulations regarding Airbnb market. It would be worthwhile for the government to understand how Airbnbs actually influence the economic success of the real estate market.

Some possible follow up questions to explore are:
- Are AirBnbs in an area bringing up/down the rent for housing prices?
- Are houses selling more or less in areas with lots of AirBnbs?
- Are AirBnbs more popular in places where rent is more expensive?
→ use correlation to help airbnb marketing, push ads in neighborhoods with criteria that make airbnb popular 


	I. Where the data is from
The information contained in this database was collected from two sources: InsideAirbnb and Zillow.
	II. Format of the data
The database is divided into three tables: airbnb, zillow_zhvi, and zillow_zri. 
The airbnb table has a row per listing, while the zillow tables have a row per zipcode. All tables have a zipcode column which will allow us to do our analysis.
Airbnb
This table lists all of the information about Airbnb listings from ten selected cities. Each line of the file contains information about a particular listing in a given city.
1. index (INTEGER): The index of the listing in this table.
2. id (INTEGER): The ID associated with the particular listing. This is a required field.
3. last_scraped (TEXT): The date that the data for this listing was collected. This is a required field.
4. street (TEXT): The name of the street that the listing is on.
5. neighbourhood_cleansed (TEXT): The name of the neighborhood that the listing is located in.
6. city (TEXT): The city that the listing is in.
7. state (TEXT): The state that the listing is in.
8. zipcode (INTEGER): The zipcode for the listing. This is a required field.
9. latitude (REAL): 	The latitude associated with the listing.
10. longitude (REAL): The longitude associated with the listing.
11. accommodates (INTEGER): The number of people that the listing can accommodate.
12. bathrooms (REAL): The number of bathrooms that the listing has.
13. bedrooms (REAL): The number of bedrooms that the listing has.
14. beds (REAL): The number of beds that the listing has.
15. price (REAL): The price that an individual has to pay to rent the listing. This is a required field.
16. weekly_price (REAL): The discounted price an individual has to pay for staying a full 7 nights.
17. monthly_price (REAL): The discounted price an individual has to pay for staying a full 30 nights.
18. security_deposit (REAL): The security deposit that an individual has to pay for the listing.
19. cleaning_fee (REAL): The cleaning fees that an individual has to pay when renting this listing.
20. minimum_nights (INTEGER): The minimum number of nights that an individual has to rent the listing for.
21. maximum_nights (INTEGER): The maximum number of nights that an individual has to rent the listing for.
22. calendar_updated (TEXT): The number of days, weeks or months since the listing had been updated.
23. availability_30 (INTEGER): The number of days that the listing has been available in the last 30 days.
24. availability_60 (INTEGER): The number of days that the listing has been available in the last 60 days.
25. availability_90 (INTEGER): The number of days that the listing has been available in the last 90 days.
 
Zillow_zhvi
The Zillow Housing Value Index (ZHVI) is a housing value estimate created and calculated by Zillow, the world’s largest real estate listing website. Each column after the first four represent the average ZHVI for a given zipcode during a given month.  (For more information, see https://www.zillow.com/research/data/)
1. index (INTEGER): The zipcode for the listing. Not to be confused with the housing value index, which has its monthly value listed in the columns below.
2. zipcode (INTEGER): The zip code over which the ZHVI average is calculated.
3. city (TEXT): The city that the listing is in.
4. state (TEXT): The state that the listing is in.
5. 2015-01 (REAL)
6. 2015-02 (REAL)
7. 2015-03 (REAL)
8. 2015-04 (REAL)
9. 2015-05 (REAL)
10. 2015-06 (REAL)
11. 2015-07 (REAL)
12. 2015-08 (REAL)
13. 2015-09 (REAL)
14. 2015-10 (REAL)
15. 2015-11 (REAL)
16. 2015-12 (REAL)
17. 2016-01 (REAL)
18. 2016-02 (REAL)
19. 2016-03 (REAL)
20. 2016-04 (REAL)
21. 2016-05 (REAL)
22. 2016-06 (REAL)
23. 2016-07 (REAL)
24. 2016-08 (REAL)
25. 2016-09 (REAL)
26. 2016-10 (REAL)
27. 2016-11 (REAL)
28. 2016-12 (REAL)
29. 2017-01 (REAL)
30. 2017-02 (REAL)
31. 2017-03 (REAL)
32. 2017-04 (REAL)
33. 2017-05 (REAL)
34. 2017-06 (REAL)
35. 2017-07 (REAL)
36. 2017-08 (REAL)
37. 2017-09 (REAL)
38. 2017-10 (REAL)
39. 2017-11 (REAL)
40. 2017-12 (REAL)
41. 2018-01 (REAL)
42. 2018-02 (REAL)
43. 2018-03 (REAL)
44. 2018-04 (REAL)
45. 2018-05 (REAL)
46. 2018-06 (REAL)
47. 2018-07 (REAL)
48. 2018-08 (REAL)
49. 2018-09 (REAL)
50. 2018-10 (REAL)
51. 2018-11 (REAL)
52. 2018-12 (REAL)
53. 2019-01 (REAL)
54. 2019-02 (REAL)
55. 2019-03 (REAL)
56. 2019-04 (REAL)
57. 2019-05 (REAL)
58. 2019-06 (REAL)
59. 2019-07 (REAL)
60. 2019-08 (REAL)
61. 2019-09 (REAL)
62. 2019-10 (REAL)
63. 2019-11 (REAL)
64. 2019-12 (REAL)
65. 2020-01 (REAL)
 
Zillow_zri
The Zillow Rental Index (ZHVI) is a rental value estimate created and calculated by Zillow, the world’s largest real estate listing website. Each column after the first four represent the average ZHVI for a given zipcode during a given month. (For more information, see https://www.zillow.com/research/data/)
1. index (INTEGER): The zipcode for the listing. Not to be confused with the rental index, which has its monthly value listed in the columns below.
2 .zipcode (INTEGER): The zip code over which the ZRI average is calculated.
3. city (TEXT): The city that the listing is in.
4. state (TEXT): The state that the listing is in.
5. 2015-01 (REAL)
6. 2015-02 (REAL)
7. 2015-03 (REAL)
8. 2015-04 (REAL)
9. 2015-05 (REAL)
10. 2015-06 (REAL)
11. 2015-07 (REAL)
12. 2015-08 (REAL)
13. 2015-09 (REAL)
14. 2015-10 (REAL)
15. 2015-11 (REAL)
16. 2015-12 (REAL)
17. 2016-01 (REAL)
18. 2016-02 (REAL)
19. 2016-03 (REAL)
20. 2016-04 (REAL)
21. 2016-05 (REAL)
22. 2016-06 (REAL)
23. 2016-07 (REAL)
24. 2016-08 (REAL)
25. 2016-09 (REAL)
26. 2016-10 (REAL)
27. 2016-11 (REAL)
28. 2016-12 (REAL)
29. 2017-01 (REAL)
30. 2017-02 (REAL)
31. 2017-03 (REAL)
32. 2017-04 (REAL)
33. 2017-05 (REAL)
34. 2017-06 (REAL)
35. 2017-07 (REAL)
36. 2017-08 (REAL)
37. 2017-09 (REAL)
38. 2017-10 (REAL)
39. 2017-11 (REAL)
40. 2017-12 (REAL)
41. 2018-01 (REAL)
42. 2018-02 (REAL)
43. 2018-03 (REAL)
44. 2018-04 (REAL)
45. 2018-05 (REAL)
46. 2018-06 (REAL)
47. 2018-07 (REAL)
48. 2018-08 (REAL)
49. 2018-09 (REAL)
50. 2018-10 (REAL)
51. 2018-11 (REAL)
52. 2018-12 (REAL)
53. 2019-01 (REAL)
54. 2019-02 (REAL)
55. 2019-03 (REAL)
56. 2019-04 (REAL)
57. 2019-05 (REAL)
58. 2019-06 (REAL)
59. 2019-07 (REAL)
60. 2019-08 (REAL)
61. 2019-09 (REAL)
62. 2019-10 (REAL)
63. 2019-11 (REAL)
64. 2019-12 (REAL)
65. 2020-01 (REAL)
 

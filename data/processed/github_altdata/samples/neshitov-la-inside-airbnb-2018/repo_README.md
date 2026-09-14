# Los Angeles airbnb listings analysis
## Installations.
Project consists of Python3 notebook that uses the following libraires:
- standard libraries numpy, pandas, scikit-learn, scipy, matplotlib,
- [geopandas](http://geopandas.org/) to work with geographical data, [colour](https://pypi.org/project/colour/) and [gmplot](https://pypi.org/project/gmplot/) for visualization,
- [CatBoost](https://catboost.ai/), a library for decision tree gradient boosting.

## Project motivation.
Airbnb is a popular service for short term rentals. To post a listing, every host goes 
through step-by-step procedure decribing the property. This generates a good amount of 
well-structured data, available at [http://insideairbnb.com/get-the-data.html](http://insideairbnb.com/get-the-data.html)
The task of  predicting a price of a listing based on its features seems to be complex and at the same time well suitable for machine learning. In this notebook I analyze the dataset that contains information about 40k Los Angeles airbnb listings (of December 6, 2018). The dataset contains the features describing the host, the property, the location, and the price. I try to find out what features affect the price most and predict the price (give a point prediction and interval prediction) based on the listing features.

## Files description.
There is one notebook with analysis, two data files and three html files with visualiztion:
- Data files: listings.csv available at [http://data.insideairbnb.com/united-states/ca/los-angeles/2018-12-06/data/listings.csv.gz](http://data.insideairbnb.com/united-states/ca/los-angeles/2018-12-06/data/listings.csv.gz) contains all the infromation about the listings; neighbourhoods.geojson is an auxiliary file with geographical information.
- html visualiztion files 

## Results
- Several statistical hypothesis are checked. I check the what is the difference in price distribution for listings owned  hosts with 'super-host' status and hosts without this 'status'. It turns out that the average prices are not significantly different, but with with 96% confidence the mean of the listings with 'super-host' status is 8$ more that the mean of the rest of the population. Also the average price of listings without reviews is 18$ more than the average price of listings without review, and average price of listings with strict cancellation policy is 35$ more than average price of listings with flexible cancellation policy with 98% confidence.

- Two prediction models are constructed. The first model predicts the price of a listing based on its features. As we should not expect that the features can determine the price completely (as there can be many other factors that we have no knowledge of) it seems important to be able to predict an interval where the price lies, rather than to give a point prediction. The second model predicts the radius of such interval. In statistical terms, the values of the features determine conditional distribution of the price, then the first model approximates the mean of the conditional price distribution, and the second model approximates its standard deviation. It turns out that the most accurate models can be obtained using gradient boosting on decision trees. I tried to construct a more complicated model using a 4 layer fully connected neural network for prediction of the entire conditional distribution, but the mor complicated model turned out to be less accurate than  the gradient boosting model.

## Licensing and Acknowledgements
Data licensing information is available at [http://insideairbnb.com/get-the-data.html](http://insideairbnb.com/get-the-data.html). Please feel free to use the code from this notebook.

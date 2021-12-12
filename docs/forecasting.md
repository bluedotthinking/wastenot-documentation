# Forecasting

<!-- For full documentation visit [mkdocs.org](https://www.mkdocs.org). -->

Making forecasts is a key functionality - the API provides a forward view of how many units to deliver/make ready
at a certain datetime, to maximise our revenue or profits


## Pre-Requisites

* Sign up for an account for [WasteNot](https://www.bluedotthinking.com)
* Located the account's API key in the [Subscription](https://www.bluedotthinking.com/subscriptions) tab

## Running a Forecast

To make a forecast, attach the inputs to a POST query and send a request to the API URL.

	https://api.bluedotthinking.com/forecast

The request has a number of required parameters - some are required, and some are optional.

At a minimum, the request requires historical data (dates, units demand), and the price and cost per unit - this returns a forecast.

### Required Inputs

* `timestamp` - an array of timestamps  in ISO-8601 format, indicating the start of the period.  This is historical data, used to generate the forecast.
* `demand` - an array of integers, matched to the number of timestamps.  This is historical data, used to generate the forecast.
* `sale_price` - the amount in local currency that one unit generates in terms of revenue
* `cost` - the amount in local currency that one unit costs to supply
* `shelf_life_seconds` - the shelf life of each item from the time it is delivered, in seconds


### Constructing a Request

First, a basic example to get us started - we will use the minimum required inputs, optimising for profit:

Here, we're using a number of default parameters that:

* c.40 days of daily demand data
* Generates a forecast assuming a replenishment on the next day
* For a product that has a shelf-life of 2 days, costs $1, and can be sold for $5
* Optimising for maximum profit - defined as revenue minus cost

####Example Request

	{
	"timestamp": ["2018-07-01","2018-07-02","2018-07-03","2018-07-04","2018-07-05",
					"2018-07-06","2018-07-07","2018-07-08","2018-07-09","2018-07-10",
					"2018-07-11","2018-07-12","2018-07-13","2018-07-14","2018-07-15",
					"2018-07-16","2018-07-17","2018-07-18","2018-07-19","2018-07-20",
					"2018-07-21","2018-07-22","2018-07-23","2018-07-24","2018-07-25",
					"2018-07-26","2018-07-27","2018-07-28","2018-07-29","2018-07-30",
					"2018-07-31","2018-08-01","2018-08-02","2018-08-03","2018-08-04",
					"2018-08-05","2018-08-06","2018-08-07","2018-08-08","2018-08-09",
					"2018-08-10"
					],
				"demand": [
					1192,1131,838,1462,1483,
					2028,1202,1004,1323,1190,
					1432,1646,1865,1669,995,
					1368,1037,1212,1274,2216,
					1204,1298,1302,1792,1376,
					1527,1807,1419,1226,1380,
					1316,1255,1429,2280,1384,
					1052,1281,1237,1508,1551,
					1913
				],
				"cost": 1,
				"sale_price": 5,
				"shelf_life_seconds": 172800.0
	}

#### Example Response

	{
	  "status": "success",
	  "forecast_timestamp": [
		"2018-08-11",
		"2018-08-12"
	  ],
	  "predicted_demand_units": [
		1434,
		1196
	  ],
	  "optimised_demand_units": [
		1493,
		1245
	  ],
	  "replenishment_timestamp": [
		"2018-08-11"
	  ],
	  "replenishment_units": [
		2738
	  ]
	}


The most important part of the JSON payload tell us how much to deliver, and when.  
This is defined by the following parameters:

* `replenishment_timestamp` - This is the timestamp associated with the replenishment.
* `replenishment_units` - Number of units replenished at this timestamp

For example, the calculation indicates we should deliver 2738 units on 2018-08-11, to maximise profit - this accounts for revenue and cost, including the potential for wastage.

For those who want to delve further, the forecast for each date relevant to the forecast is also provided.

* `forecast_timestamp` - This is the timestamp associated with the beginning of the forecast period
* `predicted_demand_units` - The "central estimate" of the forecast demand for this period - WITHOUT the optimised buffer applied
* `optimised_demand_units` - The "optimal estimate" of the forecast demand for this period - WITH the optimised buffer applied

#### Visualizing Results

See our [Example Notebooks](code_examples_python.md) for how to visualise these results, using Python.

# Forecasting

<!-- For full documentation visit [mkdocs.org](https://www.mkdocs.org). -->

Making forecasts is a key functionality - the API provides a forward view of how many units to deliver/make ready
at a certain datetime, to maximise our revenue or profits


## Pre-Requisites

* Sign up for a free account on WasteNot
* Subscribe to one of the paid plans - free 30-day trials are available
* Located the account's API key in the "Subscription" navigation tab

## Running a Forecast

To make a forecast, attach the inputs to a POST query and send a request to the API URL.

	https://api.bluedotthinking.com/forecast

The request has a number of required parameters - some are required, and some are optional.

At a minimum, the request requires historical data (dates, units demand), and the price and cost per unit


### Required Inputs

* `timestamp` - an array of timestamps  in ISO-8601 format, indicating the start of the period.  This is historical data, used to generate the forecast.
* `demand` - an array of integers, matched to the number of timestamps.  This is historical data, used to generate the forecast.
* `sale_price` - the amount in local currency that one unit generates in terms of revenue
* `cost` - the amount in local currency that one unit costs to supply
* `shelf_life_seconds` - the shelf life of each item from the time it is delivered, in seconds
* `opt_param` - the optimisation parameter - this can be either `profit` or `revenue`


### Constructing a Request

First, a basic example to get us started - we will use the minimum required inputs, optimising for profit:

Here, we're using a number of default parameters that:

* 30 days of daily demand data
* Generates a forecast for the next 7 timesteps (days)
* A delivery is made every day of the week
* For a product that has a shelf-life of 2 days, costs $1, and can be sold for $5
* Optimising for maximum profit - defined as revenue minus cost

####Example Request

	{
		"timestamp": ["2017-05-24T00:00:00", "2017-05-25T00:00:00", "2017-05-26T00:00:00", "2017-05-27T00:00:00", "2017-05-28T00:00:00", "2017-05-29T00:00:00", "2017-05-30T00:00:00", "2017-05-31T00:00:00", "2017-06-01T00:00:00", "2017-06-02T00:00:00", "2017-06-03T00:00:00", "2017-06-04T00:00:00", "2017-06-05T00:00:00", "2017-06-06T00:00:00", "2017-06-07T00:00:00", "2017-06-08T00:00:00", "2017-06-09T00:00:00", "2017-06-10T00:00:00", "2017-06-11T00:00:00", "2017-06-12T00:00:00", "2017-06-13T00:00:00", "2017-06-14T00:00:00", "2017-06-15T00:00:00", "2017-06-16T00:00:00", "2017-06-17T00:00:00", "2017-06-18T00:00:00", "2017-06-19T00:00:00", "2017-06-20T00:00:00", "2017-06-21T00:00:00", "2017-06-22T00:00:00"], 
		"demand": [559, 1407, 1727, 930, 642, 1135, 527, 1084, 1132, 1687, 978, 695, 769, 748, 1007, 1187, 1667, 1407, 774, 622, 492, 940, 1083, 1720, 918, 1069, 780, 1282, 918, 1511],
		"cost": 1, "sale_price": 5, 
		"shelf_life_seconds": 172800.0, 
		"opt_param": "profit",
		"delivery_dayofweek": [0,1,2,3,4,5,6],
		"forecast_periods_ahead":7
	}

#### Example Response

	{
		"status": "success",
		"forecast_timestamp": [
			"2017-06-23",
			"2017-06-24",
			"2017-06-25",
			"2017-06-26",
			"2017-06-27",
			"2017-06-28",
			"2017-06-29"
		],
		"backcast_delivery_timestamp": null,
		"backcast_delivery_units": null,
		"predicted_demand_units": [
			1808.0,
			1166.0,
			903.0,
			934.0,
			870.0,
			1031.0,
			1393.0
		],
		"optimised_demand_units": [
			1798.0,
			1160.0,
			898.0,
			929.0,
			865.0,
			1025.0,
			1386.0
		],
		"delivery_timestamp": [
			"2017-06-23",
			"2017-06-24",
			"2017-06-25",
			"2017-06-26",
			"2017-06-27",
			"2017-06-28",
			"2017-06-29",
			"2017-06-30",
			"2017-07-01"
		],
		"delivery_units": [
			1798.0,
			1160.0,
			898.0,
			929.0,
			865.0,
			1025.0,
			1386.0,
			1841.0,
			1203.0
		]
	}


The most important part of the JSON payload tell us how much to deliver, and when.  
This is defined by the following parameters:

* `delivery_timestamp` - This is the timestamp associated with the delivery - for a daily delivery, this is 12am of each day.
* `delivery_units` - Number of units delivered at this timestamp

For example, the calculation indicates we should deliver 1808 units on 2017-06-23, to maximise profit - this accounts for revenue and cost, including the potential for wastage.

For those who want to delve further, the forecast for each periods is also provided - in this case, every day for the next 7 days.

* `forecast_timestamp` - This is the timestamp associated with the beginning of the forecast period - for a daily forecast, this is 12am of each day!
* `predicted_demand_units` - The "central estimate" of the forecast demand for this period - this number is NOT optimised to maximise your revenue or profit.
* `optimised_demand_units` - The "optimal estimate" of the forecast demand for this period - this number IS optimised to maximise your revenue or profit, depending on the option you picked in the request.

#### Visualizing Results

The [Forecasting Example](https://nbviewer.jupyter.org/github/alvin-chan/bdt_django_front_end_postgres_mkdocs/blob/master/code_examples/forecast_example_1.ipynb?flush_cache=true) jupyter notebook provides a worked example for displaying this data using python
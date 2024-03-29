# Code Examples - Python

[WasteNot Forecast Scenario Examples, using Python 3 in a Jupyter Notebook](https://nbviewer.org/github/bluedotthinking/wastenot-documentation/blob/master/code_examples/forecast_examples.ipynb).

A number of example scenarios are provided for an example item with a unit cost of $1, sale-price of $5, with:

* Varying Item Shelf-Life
* Different Replenishment Schedules (e.g. next replenishment, periodic replenishment points, custom dates)
* Changing levels of stock-on-hand, and the expiry date for each batch
* Different forecasting periods (e.g. forecasting for the week ahead, vs. information for the next replenishment only)
* Including Events


[WasteNot Benefit Assessment, using Python 3 in a Jupyter Notebook](https://nbviewer.org/github/bluedotthinking/wastenot-documentation/blob/master/code_examples/wastenot_calculate_benefits.ipynb).

In this example, a week-ahead forecast is simulated for an item with a one-day shelf life, daily replenishments and variable demand.

Compared to an unoptimised, unbuffered forecast, WasteNot helps achieve:

* Significant improvement in Service Levels (91% -> 98% of demand satisfied)
* Increase in Profit ($117K -> $122K, an improvement of $5K over 28 days)


<!-- 
* [Forecasting Example 1](https://nbviewer.jupyter.org/github/bluedotthinking/wastenot-documentation/blob/master/code_examples/forecast_example_1.ipynb?flush_cache=true) 

	Restaurant forecasting the next 7 days, for an item with shelf-life of 2 days, with daily deliveries

* [Forecasting Example 2](https://nbviewer.jupyter.org/github/bluedotthinking/wastenot-documentation/blob/master/code_examples/forecast_example_2.ipynb?flush_cache=true) 

	Restaurant forecasting the next 7 days, for an item with shelf-life of 2 days, with daily deliveries.  There is excess stock-on-hand (3000 units, expiring in 2 days on 2018-08-12)

* [Forecasting Example 3](https://nbviewer.jupyter.org/github/bluedotthinking/wastenot-documentation/blob/master/code_examples/forecast_example_3.ipynb?flush_cache=true) 

	Restaurant forecasting the next 14 days, for an item with shelf-life of 5 days, with deliveries on Mondays and Fridays every week.

	
* [Backcasting Example](https://nbviewer.jupyter.org/github/bluedotthinking/wastenot-documentation/blob/master/code_examples/backcast_example_1.ipynb?flush_cache=true)
	
	Backcast Simulation over 30 days, for a business forecasting 2 days ahead each time, for an item with shelf-life of 2 days, with daily deliveries.
	
	Approx $6,000/month of cost savings and profit improvement vs business-as-usual (wasting 20% of all delivered units)
	
	
 -->
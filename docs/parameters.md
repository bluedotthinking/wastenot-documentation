# Query Object Parameters

| Request Object    				  | Values | Description     |
| :---      						  |    :----:   |    ---: |
| timestamp     					  | ['2018-07-01','2018-07-02','2018-07-03']   | ***[Required] List of Strings*** - Contains the datetime of the historical demand.  Must be in ISO8601 format (YYYY-MM-DD)  |
| demand 							  | [1192,1131,838] | ***[Required] List of Integers/Floats*** - Contains the demanded units for each historical period  |
| cost 								  | 1      | ***[Required] Float*** - Cost for one unit of the item |
| sale_price  			 		 	  | 5      | ***[Required] Float*** - Sale Price for one unit of the item |
| shelf_life_seconds  	  			  | 172800      | ***[Required] Integer*** - Shelf Life of the item, in seconds |
| replenishment_schedule 			  | 'next_timestep','periodic','custom_dates' | ***[Optional] String*** - Replenishment schedule - defaults to <em>'next_timestep'</em> (replenish the day after the historical data if not specified).  <em>'periodic'</em> is for regular replenishments throughout a week. <em>'custom_dates'</em> is for defining specific replenishment dates |
| replenishment_dayofweek 			  | [0,1,2,3,4,5,6]  | ***[Optional] List of Integers*** - Only used when replenishment_schedule is ***'periodic'***, specifies the days of the week when replenishment occurs.  Values between 0 (for Monday) and 6 (for Sunday) |
| future_replenishment_datetimes   	  | ['2018-08-13','2018-08-15'] | ***[Optional] List of Strings*** - Only used when replenishment_schedule is ***'custom_dates'***, specifies the dates when replenishment occurs.  Must be in ISO8601 format (YYYY-MM-DD) |
| forecast_start_datetime   		  | '2018-08-13'  | ***[Optional] String*** -  Only used when replenishment_schedule is ***'periodic'***.  Start point for range of dates for which to generate replenishments.  Must be in ISO8601 format (YYYY-MM-DD)  |
| forecast_end_datetime  			  | '2018-08-19'  | ***[Optional] String*** -  Only used when replenishment_schedule is ***'periodic'***.  End point for range of dates for which to generate replenishments |
| stock_expiry_datetimes 			  | ['2018-08-13','2018-08-16'] | ***[Optional] List of Strings*** - Contains the expiry datetimes for batches of Stock-on-Hand.  Must be in ISO8601 format (YYYY-MM-DD) |
| stock_available_units			      | [500,2500] | ***[Optional] List of Integers/Floats*** - Contains the units for each batch of Stock-on-Hand in stock_expiry_datetimes |


# Response Object Parameters

| Response Object      			| Values 	  | Description     |
| :---        					|    :----:   |          :--- |
| status      					| <em>success</em> or <em>failure</em> 	 | ***String*** - returns status of the request |
| replenishment_timestamp       | ['2018-08-11','2018-08-12']       | ***List of Strings*** - returns the datetime of the replenishments  |
| replenishment_units      		| [1578, 1304]       | ***List of Integers/Floats*** - returns the replenishment quantity corresponding to each element in replenishment_timestamp |
| forecast_timestamp   			|['2018-08-11','2018-08-12',...]  |  ***List of Strings*** - returns the timestamp for each forecast time period|
| predicted_demand_units     	|[1434, 1196,...]       | ***List of Integers/Floats*** - returns the predicted demand (without buffer) for each element in forecast_timestamp |
| optimised_demand_units        | [1578, 1304] | ***List of Integers/Floats*** - returns the predicted demand (with buffer applied) for each element in forecast_timestamp |

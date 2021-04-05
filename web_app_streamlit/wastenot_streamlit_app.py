import streamlit as st
import pandas as pd
import os
import altair as alt
from datetime import datetime
import base64


import streamlit as st
import streamlit.components.v1 as stc

# File Processing Pkgs
import pandas as pd
import json
import requests

import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio



def get_table_download_link(df):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/csv;base64,{b64}">Download csv file</a>'
    

def main():
	st.sidebar.title("WasteNot")	

	menu = ["Home","Forecast","Backcast"]
	choice = st.sidebar.selectbox("Navigation",menu)
	access_token = st.sidebar.text_input('Access Token', 'abcdefghijk123456')	

	if choice == "Home":
	
		st.title("Home - About This Tool")		
		st.write('Welcome to the web application for WasteNot - an example of how to perform forecast and backcasts for perishable food items to reduce waste and increase profits')
		st.write('Before starting, please ensure you have signed up for an account at [https://www.bluedotthinking.com](https://www.bluedotthinking.com) and retrieved your access token from the Subscription tab')
		st.write('There are 2 key functionalities:')		
		st.write("- Forecast: Generate an optimised forecast, based on the historical demand, and the item's attributes.  This requires subscription to a paid plan - 30-day free trial is available.")
		st.write("- Backcast: Calculate the business benefits WasteNot could have brought, based on the historical demand, and the item's attributes.  This does not require subscription to a paid plan.")
		st.write('In either case, the user can either:')
		st.write('- Use an example file containing daily demand, for a 12-month period')		
		st.write('- Upload your own data file containing historical daily demand')		

	elif choice == "Forecast":

		st.title("Forecast")	

		file_upload_selector = ["Use Example File","Upload A File"]
		upload_file_choice = st.sidebar.selectbox("Time Series Data", file_upload_selector)
		
		if upload_file_choice == "Use Example File":
			data_file = 'https://raw.githubusercontent.com/bluedotthinking/wastenot-documentation/master/example_data/bdt_example_input.csv'

		if upload_file_choice == "Upload A File":
			data_file = st.sidebar.file_uploader("Upload CSV",type=['csv'])
			st.write('The file you upload with historical demand data must have 2 columns - "date" and "demand_units"')
			st.write('- The "date" column should have dates in the format YYYY-MM-DD')			
			st.write('- The "demand_units" column should only container integers (whole numnbers)')						

			example_data_file = 'https://raw.githubusercontent.com/bluedotthinking/wastenot-documentation/master/example_data/bdt_example_input.csv'
			example_input_df = pd.read_csv(example_data_file)							
			csv = example_input_df.to_csv(index=False)
			b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
			href = f'<a href="data:file/csv;base64,{b64}" download="example_input.csv">Download Example Inputs in CSV format</a>'
			st.markdown('- '+href, unsafe_allow_html=True)			
			

		opt_param = st.sidebar.selectbox(
			"What would you like to maximise?",
			("profit", "revenue"),
			help='Choosing revenue tends to result in large safe stock levels, when events relating to high demand are not identified.'
			)			
		unit_cost = st.sidebar.number_input('Unit Cost', value=1.00)
		unit_sell_price= st.sidebar.number_input('Unit Cost', value=5.00)
		currency_symbol = st.sidebar.text_input("Currency symbol", '$')
		forecast_ahead_periods = st.sidebar.number_input('Periods (days) to Forecast Ahead For', 
						min_value=1,
						max_value = 14,
						value=7,
						step = 1)
		shelf_life_days = st.sidebar.number_input('Shelf Life In Days', 
						min_value=1,
						max_value = 30,
						value=3,
						step = 1)	
		shelf_life_seconds = shelf_life_days*3600*24

		percentage_wasted = st.sidebar.slider('Percentage of Delivered units Wasted (Historical)', 0, 100, 20, 1)						
		fraction_wasted = float(percentage_wasted)/100.
		replenishment_daysofweek = st.sidebar.multiselect('What days of the week are your replenishments?',
		['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'],
		['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'])
		
		dow_mapping = {'Monday':0,
						'Tuesday':1,
						'Wednesday':2,
						'Thursday':3,
						'Friday':4,
						'Saturday':5,
						'Sunday':6
						}
						
		replenishment_daysofweek = [dow_mapping[dow] for dow in replenishment_daysofweek]
		
		st.write('Perform a forecast with the provided data, with a unit cost of',currency_symbol,unit_cost,
				 ', unit sell-price of',currency_symbol,unit_sell_price,
				 ', for the next',forecast_ahead_periods,'periods (days)')
		if st.button("Run Forecast"):
			if data_file is not None:
				if upload_file_choice == "Upload A File":
					file_details = {"Filename":data_file.name,"FileType":data_file.type,"FileSize":data_file.size}
					df = pd.read_csv(data_file)
				if upload_file_choice == "Use Example File":
					df = pd.read_csv(data_file)

				st.dataframe(df)
				

				fig_input = go.Figure()
				fig_input.update_layout(title="Historical Demand Data")
				fig_input.add_trace(
					go.Bar(x=df['date'].values, y=df['demand_units'].values,
						   name="Training Data"))
				st.plotly_chart(fig_input, use_container_width=True)
				
				payload_dict = {'timestamp':list(df['date'].values),
								'demand':[int(dd) for dd in df['demand_units'].values],
								"cost": float(unit_cost), 
								"sale_price": float(unit_sell_price), 
								"shelf_life_seconds": int(shelf_life_seconds), 
								"opt_param": opt_param,
								"forecast_periods_ahead":int(forecast_ahead_periods),
								"replenishment_dayofweek": replenishment_daysofweek,
								"fraction_wasted": float(fraction_wasted)}

				payload_json = json.dumps(payload_dict)
				url = "https://api.bluedotthinking.com/forecast"
				
				headers = {
				  'access_token': access_token,
				  'Content-Type': 'application/json'
				}

				try:
					response = requests.request("POST", url, headers=headers, data=payload_json)
					json_data = json.loads(response.text)
					
					delivery_df = pd.DataFrame(data={'timestamp':json_data['delivery_timestamp'],
													 'delivered_units':json_data['delivery_units']
													})					
					delivery_df['timestamp'] = pd.to_datetime(delivery_df['timestamp'])
													
					forecast_df = pd.DataFrame(data={'timestamp': json_data['forecast_timestamp'],
													 'predicted_demand_units': json_data['predicted_demand_units'],
													 'optimised_demand_units': json_data['optimised_demand_units'],
													})													
					forecast_df['timestamp'] = pd.to_datetime(forecast_df['timestamp'])													

					st.write('Forecast Successful, Response code:',response.status_code)						
					fig_output = go.Figure()
					fig_output.update_layout(title="Forecast Demand")
					fig_output.add_trace(
						go.Bar(x=delivery_df['timestamp'], 
							   y=delivery_df['delivered_units'],
							   name="Optimised Replenishments"))

					fig_output.add_trace(
						go.Bar(x=forecast_df['timestamp'], 
							   y=forecast_df['predicted_demand_units'],
							   name="Central Forecast Estimate"))

					st.plotly_chart(fig_output, use_container_width=True)


				except:
					st.write('Forecast Failed, Response code:',response.status_code, ', Error message:',response.text)		

			merged_df = pd.merge(delivery_df, forecast_df, on = 'timestamp', how='outer').fillna(0).sort_values('timestamp', ascending=True)

			csv = merged_df.to_csv(index=False)
			b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
			href = f'<a href="data:file/csv;base64,{b64}" download="replenishment.csv">Download Results in CSV format</a>'
			st.markdown(href, unsafe_allow_html=True)
		
	elif choice == "Backcast":
	
		st.title("Backcast")		
		file_upload_selector = ["Use Example File","Upload A File"]
		upload_file_choice = st.sidebar.selectbox("Time Series Data", file_upload_selector)
		example_data_file = 'https://raw.githubusercontent.com/bluedotthinking/wastenot-documentation/master/example_data/bdt_example_input.csv'
		
		if upload_file_choice == "Use Example File":
			data_file = 'https://raw.githubusercontent.com/bluedotthinking/wastenot-documentation/master/example_data/bdt_example_input.csv'

		if upload_file_choice == "Upload A File":
			data_file = st.sidebar.file_uploader("Upload CSV",type=['csv'])

			
			st.write('The file you upload with historical demand data must have 2 columns - "date" and "demand_units"')
			st.write('- The "date" column should have dates in the format YYYY-MM-DD')			
			st.write('- The "demand_units" column should only container integers (whole numnbers)')

			example_data_file = 'https://raw.githubusercontent.com/bluedotthinking/wastenot-documentation/master/example_data/bdt_example_input.csv'
			example_input_df = pd.read_csv(example_data_file)							
			csv = example_input_df.to_csv(index=False)
			b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
			href = f'<a href="data:file/csv;base64,{b64}" download="example_input.csv">Download Example Inputs in CSV format</a>'
			st.markdown('- '+href, unsafe_allow_html=True)


		opt_param = st.sidebar.selectbox(
			"What would you like to maximise?",
			("profit", "revenue"),
			help='Choosing "revenue" for this options results in higher values - the system is attempting to maximise revenue, even for known events relating to high demand.'
			)			
		unit_cost = st.sidebar.number_input('Unit Cost', value=1.00)
		unit_sell_price= st.sidebar.number_input('Unit Cost', value=5.00)
		currency_symbol = st.sidebar.text_input("Currency symbol", '$', help='Currency symbol for cost/sell-price')
		forecast_ahead_periods = st.sidebar.number_input('Periods (days) to Forecast Ahead For', 
						min_value=1,
						max_value = 14,
						value=7,
						step = 1)
		shelf_life_days = st.sidebar.number_input('Shelf Life In Days', 
						min_value=1,
						max_value = 30,
						value=3,
						step = 1)	
		shelf_life_seconds = shelf_life_days*3600*24
		n_forecasts_simulated = st.sidebar.number_input('Number of Forecasts Made', 
						min_value=1,
						max_value = 20,
						value=5,
						step = 1)
		n_training_periods = st.sidebar.number_input('Number of Periods to use for Training', 
						min_value=1,
						max_value = None,
						value=100,
						step = 1)

		fraction_wasted = 0.2
		options = st.sidebar.multiselect('What days of the week are your replenishments?',
		['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'],
		['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'])
		n_periods_simulated = int(forecast_ahead_periods*n_forecasts_simulated)
		st.write('Perform a backcast with the provided file, with a unit cost of',
					currency_symbol,unit_cost,', unit sell-price of',currency_symbol,unit_sell_price,', and a shelf-life of',shelf_life_days,'days.  Carrying out,',n_forecasts_simulated,'forecasts, forecasting',forecast_ahead_periods,'periods (days) ahead each time')		
		if st.button("Run Backcast"):
			if data_file is not None:
				if upload_file_choice == "Upload A File":
					file_details = {"Filename":data_file.name,"FileType":data_file.type,"FileSize":data_file.size}
					input_df = pd.read_csv(data_file)
				if upload_file_choice == "Use Example File":
					input_df = pd.read_csv(data_file)				

				payload_dict = {'timestamp':list(input_df['date'].values),
								'demand':[int(dd) for dd in input_df['demand_units'].values],
								"cost": float(unit_cost), 
								"sale_price": float(unit_sell_price), 
								"shelf_life_seconds": int(shelf_life_seconds), 
								"opt_param": opt_param,
								"forecast_periods_ahead":int(forecast_ahead_periods),
								"replenishment_dayofweek": [0,1,2,3,4,5,6],
								"n_training_periods": int(n_training_periods),
								"n_forecasts_simulated": int(n_forecasts_simulated),
								"fraction_wasted": float(fraction_wasted)}

				payload_json = json.dumps(payload_dict)

				url = "https://api.bluedotthinking.com/backcast"
				
				headers = {
				  'access_token': access_token,
				  'Content-Type': 'application/json'
				}

				try:
					response = requests.request("POST", url, headers=headers, data=payload_json)
					json_data = json.loads(response.text)
					results_df = pd.DataFrame(data={'timestamp_start':json_data['timestamp_start'],
													'timestamp_end':json_data['timestamp_end'],
													'simulation_satisfied_units':json_data['simulation_satisfied_units'],
													'simulation_delivered_units':json_data['simulation_delivered_units'],
													'simulation_unmet_units':json_data['simulation_unmet_units'],
													'simulation_wasted_units':json_data['simulation_wasted_units'],
													'actual_demand_units_unconstrained':json_data['actual_demand_units_unconstrained']
													})
					results_df['timestamp_start'] = pd.to_datetime(results_df['timestamp_start'])
					results_df['timestamp_end'] = pd.to_datetime(results_df['timestamp_end'])
					a = datetime.strptime(json_data['simulation_first_datetime'],"%Y-%m-%d")
					b = datetime.strptime(json_data['simulation_last_datetime'],"%Y-%m-%d")
					seconds_between = (b-a).total_seconds()
					days_between = (b-a).days +1
					seconds_in_week = 24*3600*7
					seconds_in_year = 24*3600*365
					months_in_year = 12
					seconds_in_month = seconds_in_year/months_in_year					

					st.write('Backcast Successful, Response code:',response.status_code)			

					st.write('Deploying the WasteNot Service on this item between {0} & {1} ({2} days) would have had the following impact:'.format(json_data['simulation_first_datetime'], json_data['simulation_last_datetime'], days_between))

					historical_demand_units_total = json_data['historical_demand_units_total']
					historical_delivered_units_total = int(historical_demand_units_total/(1.-fraction_wasted))
					historical_wasted_units_total = historical_delivered_units_total - historical_demand_units_total
					
					historical_revenue = historical_demand_units_total * unit_sell_price
					historical_cost = (historical_delivered_units_total) * unit_cost
					historical_profit = historical_revenue - historical_cost
					
					
					simulation_satisfied_units_total = json_data['simulation_satisfied_units_total']					
					simulation_wasted_units_total = json_data['simulation_wasted_units_total']
					simulation_delivered_units_total = json_data['simulation_delivered_units_total']
					simulation_leftover_units_total = json_data['simulation_delivered_units_total'] - json_data['simulation_satisfied_units_total'] - json_data['simulation_wasted_units_total']
					
					simulation_revenue = simulation_satisfied_units_total * unit_sell_price
					simulation_cost = (simulation_delivered_units_total - simulation_leftover_units_total) * unit_cost
					simulation_profit = simulation_revenue - simulation_cost

					profit_change = simulation_profit - historical_profit
					
					n_weeks_in_simulation = seconds_between/seconds_in_week
					n_months_in_simulation = seconds_between/seconds_in_month

					weekly_benefit = profit_change / n_weeks_in_simulation
					monthly_benefit = profit_change / n_months_in_simulation


					hist_kpi = [historical_profit, historical_revenue, historical_cost, json_data['historical_demand_units_total'], json_data['historical_wasted_units_total']]
					simulation_kpi = [simulation_profit, simulation_revenue, simulation_cost, json_data['simulation_satisfied_units_total'], json_data['simulation_wasted_units_total']]
					abs_change_in_kpi = [simulation_kpi[x] - hist_kpi[x] for x in range(len(simulation_kpi))]
					percentage_change_in_kpi = [100.*(simulation_kpi[x] - hist_kpi[x])/hist_kpi[x] for x in range(len(simulation_kpi))]
					percentage_change_in_kpi = [ '%.1f' % elem for elem in percentage_change_in_kpi ]

					if weekly_benefit > 0:
						benefit_colour = 'green'
					if weekly_benefit == 0:
						benefit_colour = 'orange'
					if weekly_benefit < 0:
						benefit_colour = 'red'	

					fig = go.Figure()
					fig.add_trace(go.Indicator(
						mode = "number",
						value = profit_change,    
						title = {"text": "Change in Profit<br><span style='font-size:0.8em;color:gray'>Over "+str(days_between)+" days</span>"},    
						number = {'prefix': currency_symbol,
								  'font.color': benefit_colour},
						domain = {'x': [0.0,0.475]
								  , 'y': [0.5, 1.0]
								 }
					))

					fig.add_trace(go.Indicator(
						mode = "delta",
						value = json_data['simulation_wasted_units_total'],
						title = {"text": "Units Wasted"},
						delta = {'reference': json_data['historical_wasted_units_total'], 'relative': True, 'position' : "right",
								 'increasing.color':"red",
								 'decreasing.color':"green",},
						domain = {'x': [0.525,1.0]
								  , 'y': [0.5, 1.0]
								 }
					))
					
					
					fig.add_trace(go.Indicator(
						mode = "number",
						value = weekly_benefit,
						title = {"text": "Weekly Benefit"},
						number = {'prefix': currency_symbol,
								  'font.color': benefit_colour},
						domain = {'x': [0.0,0.475]
								  , 'y': [0.0, 0.5]
								 }
					))

					fig.add_trace(go.Indicator(
						mode = "number",
						value = monthly_benefit,
						title = {"text": "Monthly Benefit"}, 
						number = {'prefix': currency_symbol,
								  'font.color': benefit_colour},
						domain = {'x': [0.525,1.0]
								  , 'y': [0.0, 0.5]
								 }
					))
					st.plotly_chart(fig, use_container_width=True)

					st.line_chart(data=results_df[['actual_demand_units_unconstrained','simulation_delivered_units']], width=0, height=0, use_container_width=True)
				
					kpi_df = pd.DataFrame(data={'KPI':['Profit','Revenue','Cost','Satisfied Units','Wasted Units'],
												'Without WasteNot':[json_data['historical_profit'], json_data['historical_revenue'], json_data['historical_cost'], json_data['historical_demand_units_total'], json_data['historical_wasted_units_total']],
												'With WasteNot':[json_data['simulation_profit'], json_data['simulation_revenue'], json_data['simulation_cost'], json_data['simulation_satisfied_units_total'], json_data['simulation_wasted_units_total']],
												'Change in KPI':abs_change_in_kpi,
												'% Change in KPI':percentage_change_in_kpi
												})

					kpi_df = pd.DataFrame(data={'KPI':['Profit','Revenue','Cost','Satisfied Units','Wasted Units'],
												'Without WasteNot':hist_kpi,
												'With WasteNot':simulation_kpi,
												'Change in KPI':abs_change_in_kpi,
												'% Change in KPI':percentage_change_in_kpi
												})



					st.table(kpi_df)			



					fig_unmet_waste = go.Figure()
					fig_unmet_waste.update_layout(title="Wasted & Unmet Units")
					fig_unmet_waste.add_trace(
						go.Bar(x=results_df['timestamp_start'], 
							   y=results_df['simulation_wasted_units'],
							   name="Wasted Units"))

					fig_unmet_waste.add_trace(
						go.Bar(x=results_df['timestamp_start'], 
							   y=results_df['simulation_unmet_units'],
							   name="Unmet Demand Units"))

					st.plotly_chart(fig_unmet_waste, use_container_width=True)
							
				except:
					st.write('Backcast Failed, Response code:',response.status_code, ', Error message:',response.text)

				st.write('Input Demand Data:')
				
				fig_input = px.bar(input_df[:n_training_periods], x='date', y=['demand_units'], title='Training Data')
				fig_input = px.bar(input_df[n_training_periods:n_training_periods+n_periods_simulated], x='date', y=['demand_units'], title='Test Demand Data')

				fig_input = go.Figure()
				fig_input.update_layout(title="Training & Test Demand Data")
				fig_input.add_trace(
					go.Bar(x=input_df['date'].values[:n_training_periods], 
							y=input_df['demand_units'].values[:n_training_periods],
						   name="Training Data"))
				fig_input.add_trace(
					go.Bar(x=input_df['date'][n_training_periods:n_training_periods+n_periods_simulated].values, 
							y=input_df['demand_units'].values[n_training_periods:n_training_periods+n_periods_simulated],
						  name="Test Data"))			
				st.plotly_chart(fig_input, use_container_width=True)
				st.dataframe(input_df)
				


	else:
		st.subheader("About")
		st.info("Built with Streamlit")



if __name__ == '__main__':
	main()
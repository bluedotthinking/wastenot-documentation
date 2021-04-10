import streamlit as st
import pandas as pd
import os
import altair as alt
from datetime import datetime
import base64
import numpy as np

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


@st.cache
def backcast_request(access_token, input_df, unit_sell_price, unit_cost, shelf_life_seconds, 
					 opt_param, forecast_ahead_periods, replenishment_dayofweek, n_training_periods, n_forecasts_simulated,
					 fraction_wasted):

	payload_dict = {'timestamp':list(input_df['date'].values),
					'demand':[int(dd) for dd in input_df['demand_units'].values],
					"cost": float(unit_cost), 
					"sale_price": float(unit_sell_price), 
					"shelf_life_seconds": int(shelf_life_seconds), 
					"opt_param": opt_param,
					"forecast_periods_ahead":int(forecast_ahead_periods),
					"replenishment_dayofweek": replenishment_dayofweek,
					"n_training_periods": int(n_training_periods),
					"n_forecasts_simulated": int(n_forecasts_simulated),
					"fraction_wasted": float(fraction_wasted)}

	payload_json = json.dumps(payload_dict)
	url = "https://api.bluedotthinking.com/backcast"
	headers = {
	  'access_token': access_token,
	  'Content-Type': 'application/json'
	}
	response = requests.request("POST", url, headers=headers, data=payload_json)
	
	return response



def calculate_benefits(results_df, json_data, fraction_wasted, unit_sell_price, unit_cost, currency_symbol):
	a = datetime.strptime(json_data['simulation_first_datetime'],"%Y-%m-%d")
	b = datetime.strptime(json_data['simulation_last_datetime'],"%Y-%m-%d")
	seconds_between = (b-a).total_seconds()
	days_between = (b-a).days +1
	seconds_in_week = 24*3600*7
	seconds_in_year = 24*3600*365
	months_in_year = 12
	seconds_in_month = seconds_in_year/months_in_year					

	fraction_wasted_array = np.arange(0,31,1)/100.
	percentage_wasted_array = np.arange(0,31,1)
	percentage_wasted_array = [str(int(x))+'%' for x in percentage_wasted_array]

	profit_change_array = []
	weekly_profit_change_array = []
	monthly_profit_change_array = []		


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

	st.write('Deploying the WasteNot Service on this item between ',json_data['simulation_first_datetime'],' & ',
			 json_data['simulation_last_datetime'],' (',days_between,' days) would have generated '+currency_symbol,int(monthly_benefit),'/month of business benefit, assuming historically',
				int(fraction_wasted*100.),'% of delivered units were wasted')


	simulation_satisfied_percentage = 100.*(simulation_satisfied_units_total/historical_demand_units_total)

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
	col1, col2 = st.beta_columns((2,1))
	with col1:
		fig_timeseries = go.Figure()
		fig_timeseries.update_layout(title="Demand vs Delivered Units",     
								 	 paper_bgcolor='rgba(0,0,0,0)',
					 			     plot_bgcolor='rgba(0,0,0,0)')
		fig_timeseries.add_trace(
			go.Line(x=results_df['timestamp_start'], 
				    y=results_df['actual_demand_units_unconstrained'],
				    name="Historical Demand",
				    marker_color='blue'))

		fig_timeseries.add_trace(
			go.Bar(x=results_df['timestamp_start'], 
				   y=results_df['simulation_delivered_units'],
				   name="Simulated Replenishments",
				   marker_color='lightblue'))
		fig_timeseries.update_layout(legend=dict(
			orientation="h",
			yanchor="bottom",
			y=1.02,
			xanchor="right",
			x=1
		))			
		st.plotly_chart(fig_timeseries, use_container_width=True)
		csv = results_df.to_csv(index=False)
		b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
		href = f'<a href="data:file/csv;base64,{b64}" download="backcast_timeseries_results.csv">Download Time-Series Results in CSV format</a>'
		st.markdown(href, unsafe_allow_html=True)
			
	with col2:
		fig = go.Figure()
		fig.add_trace(go.Indicator(
			mode = "number",
			value = profit_change,    
			title = {"text": "Business Savings"},    
			number = {'prefix': currency_symbol,
					  'font.color': benefit_colour},
			domain = {'x': [0.0,1.0]
					  , 'y': [0.75, 1.0]
					 }
		))

		fig.add_trace(go.Indicator(
			mode = "delta",
			value = json_data['simulation_wasted_units_total'],
			title = {"text": "Units Wasted"},
			delta = {'reference': json_data['historical_wasted_units_total'], 'relative': True, 'position' : "right",
					 'increasing.color':"red",
					 'decreasing.color':"green",},
			domain = {'x': [0.,1.0]
					  , 'y': [0.45, 0.65]
					 }
		))

		fig.add_trace(go.Indicator(
			mode = "number",
			value = simulation_satisfied_percentage,    
			title = {"text": "Demand Satisfied"},    
			number = {'suffix': '%',
					  'font.color': 'green'},
			domain = {'x': [0.,1.0]
					  , 'y': [0.0, 0.3]
					 }
		))
		


		st.plotly_chart(fig, use_container_width=True)
	
	kpi_df = pd.DataFrame(data={'KPI':['Profit','Revenue','Cost','Satisfied Units','Wasted Units'],
								'Without WasteNot':hist_kpi,
								'With WasteNot':simulation_kpi,
								'Change in KPI':abs_change_in_kpi,
								'% Change in KPI':percentage_change_in_kpi
								})
	st.dataframe(kpi_df)			
	csv = kpi_df.to_csv(index=False)
	b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
	href = f'<a href="data:file/csv;base64,{b64}" download="backcast_summary_results.csv">Download Summary Results in CSV format</a>'
	st.markdown(href, unsafe_allow_html=True)

	result_expander = st.beta_expander("Further Results", expanded=False)		
	with result_expander:

		fig_unmet_waste = go.Figure()
		fig_unmet_waste.update_layout(title="Backcast: Wasted & Unmet Units", 
									  legend=dict(orientation="h",
									  yanchor="bottom",
									  y=1.02,
									  xanchor="right",
									  x=1
									  ))
		fig_timeseries.update_layout()			
		
		fig_unmet_waste.add_trace(
			go.Bar(x=results_df['timestamp_start'], 
				   y=results_df['simulation_wasted_units'],
				   name="Wasted Units"))

		fig_unmet_waste.add_trace(
			go.Bar(x=results_df['timestamp_start'], 
				   y=results_df['simulation_unmet_units'],
				   name="Unmet Demand Units"))

		st.plotly_chart(fig_unmet_waste, use_container_width=True)	
		
		for fw in fraction_wasted_array:
			historical_demand_units_total = json_data['historical_demand_units_total']
			historical_delivered_units_total = int(historical_demand_units_total/(1.-fw))
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
			profit_change_array.append(profit_change)
			weekly_profit_change_array.append(weekly_benefit)
			monthly_profit_change_array.append(monthly_benefit)				
	
		fraction_wasted_colour_array = ['red' if x <=0 else 'green' for x in profit_change_array]
		fig_benefit_by_waste_fraction = go.Figure()
		fig_benefit_by_waste_fraction.update_layout(title="Business Benefit increases if the historical wastage is high", 
													legend=dict(orientation="h",
													yanchor="bottom",
													y=1.02,
													xanchor="right",
													x=1
													))
		fig_benefit_by_waste_fraction.update_traces(marker_colorbar_tickprefix="$", selector=dict(type='bar'))						
		fig_benefit_by_waste_fraction.add_trace(
			go.Bar(x=percentage_wasted_array, 
				   y=monthly_profit_change_array,
				   marker_color = fraction_wasted_colour_array,
				   hovertemplate = '<i>Historical Wastage</i>: %{x}'+'<br><b>Monthly Business Benefit</b>: %{y:$.2f}<br>',
				   name="Monthly Benefit"))
		st.plotly_chart(fig_benefit_by_waste_fraction, use_container_width=True)	


def set_simulation_params(functionality):
	col3, col4, col5, col6 = st.beta_columns((1,1,1,1))	
	with col3:
		opt_param = st.selectbox(
			"What would you like to maximise?",
			("profit", "revenue"),
			help='Choosing revenue tends to result in large safe stock levels, when events relating to high demand are not identified.'
			)			
		forecast_ahead_periods = st.number_input('Periods (days) to Forecast Ahead For', 
						min_value=1,
						max_value = 14,
						value=7,
						step = 1)
		shelf_life_days = st.number_input('Shelf Life In Days', 
						min_value=1,
						max_value = 30,
						value=3,
						step = 1)	
		shelf_life_seconds = shelf_life_days*3600*24

	with col4:

		unit_cost = st.number_input('Unit Cost', value=1.00)
		unit_sell_price= st.number_input('Unit Sell Price', value=5.00)
		currency_symbol = st.text_input("Currency symbol", '$')

	with col5:

		replenishment_daysofweek = st.multiselect('What days of the week are your replenishments?',
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
								
	with col6:
		percentage_wasted = st.slider('Percentage of Delivered units Wasted (Historical)', 0, 100, 20, 1)
		fraction_wasted = float(percentage_wasted)/100.
		
		if functionality == 'Backcast':
			n_forecasts_simulated = st.number_input('Number of Forecasts Made', 
							min_value=1,
							max_value = 20,
							value=5,
							step = 1)
			n_training_periods = st.number_input('Number of Periods to use for Training', 
							min_value=1,
							max_value = None,
							value=100,
							step = 1)
		else:
			n_forecasts_simulated = None
			n_training_periods = None

	return opt_param, unit_cost, unit_sell_price, currency_symbol, forecast_ahead_periods, shelf_life_days, shelf_life_seconds, fraction_wasted, replenishment_daysofweek, n_forecasts_simulated, n_training_periods

	

def main():
	st.sidebar.title("WasteNot")	

	menu = ["Home","Forecast","Backcast"]
	choice = st.sidebar.selectbox("Navigation",menu)
	access_token = st.sidebar.text_input('Access Token', '', help='Get your token from [https://www.bluedotthinking.com/subscriptions](https://www.bluedotthinking.com/subscriptions)')	

	if choice == "Home":
	
		st.title("Home - About This Tool")		
		st.write('Welcome to the web application for WasteNot - an example of how to perform forecast and backcasts for perishable food items to reduce waste and increase profits')
		st.write('Before starting, please ensure you have signed up for an account at [https://www.bluedotthinking.com](https://www.bluedotthinking.com) and retrieved your access token from the Subscription tab')
		st.write('There are 2 key functionalities:')		
		st.write("- Forecast: Generate an optimised forecast, based on the historical demand, and the item's attributes.  This requires subscription to a paid plan - a 30 day free trial is available.")
		st.write("- Backcast: Calculate the business benefits WasteNot could have brought, based on the historical demand, and the item's attributes.  This does not require subscription to a paid plan.")
		st.write('In both cases, the user can choose to:')
		st.write('- Use an example file containing daily demand, for a 12-month period')		
		st.write('- Upload their own data file containing historical daily demand')	
		st.write('Uploaded data is not saved, and does not persist beyond your session')
		
	elif choice == "Forecast":

		st.title("Forecast")
		input_data_expander = st.beta_expander("Historical Demand Data", expanded=True)		
		
		with input_data_expander:
			file_upload_selector = ["Use Example File","Upload A File"]

			col1, col2 = st.beta_columns(2)
			
			with col1:
				upload_file_choice = st.selectbox("Time Series Data", file_upload_selector)
			
				if upload_file_choice == "Use Example File":
					data_file = 'https://raw.githubusercontent.com/bluedotthinking/wastenot-documentation/master/example_data/bdt_example_input.csv'
					input_df = pd.read_csv(data_file)
					st.write('The example file contains historical demand data with 2 columns:')
					st.write('- "date", containing dates in the format YYYY-MM-DD')			
					st.write('- "demand_units", containing only integers (whole numbers)')									
					


				if upload_file_choice == "Upload A File":
					data_file = None
					data_file = st.file_uploader("Upload CSV",type=['csv'])
					st.write('The file you upload with historical demand data must have 2 columns:')
					st.write('- "date", containing dates in the format YYYY-MM-DD')			
					st.write('- "demand_units", containing only integers (whole numbers)')										

			with col2:

			
				if data_file is not None:
# 					file_details = {"Filename":data_file.name,"FileType":data_file.type,"FileSize":data_file.size}
					input_df = pd.read_csv(data_file)
				
					fig_input = go.Figure()
					fig_input.update_layout(title="Historical Demand Data")
					fig_input.add_trace(
						go.Bar(x=input_df['date'].values, y=input_df['demand_units'].values,
							   name="Training Data"))
					st.plotly_chart(fig_input, use_container_width=True)
# 					st.dataframe(input_df)

				else:
					st.write('Please upload some data')

		st.markdown('#')

		simulation_params_expander = st.beta_expander("Simulation Parameters", expanded=False)
		with simulation_params_expander:
			opt_param, unit_cost, unit_sell_price, currency_symbol, forecast_ahead_periods, shelf_life_days, shelf_life_seconds, fraction_wasted, replenishment_daysofweek, n_forecasts_simulated, n_training_periods = set_simulation_params(choice)
		st.markdown('#')			

		col3, col4 = st.beta_columns((1,3))
		
		with col4:
			if access_token == '':
				st.write('Get your Access Token at https://www.bluedotthinking.com/subscriptions/')
			else:
				st.write('Perform a forecast with the provided data and access token, with a unit cost of',currency_symbol,unit_cost,
						 ', unit sell-price of',currency_symbol,unit_sell_price,
						 ', for the next',forecast_ahead_periods,'periods (days)')
		with col3:


			run_triggered = False			
			if st.button("Run Forecast"):
				input_data_expander.expand=False
				run_triggered = True			

				
				payload_dict = {'timestamp':list(input_df['date'].values),
								'demand':[int(dd) for dd in input_df['demand_units'].values],
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
				response = requests.request("POST", url, headers=headers, data=payload_json)



		result_expander = st.beta_expander("Results", expanded=True)		
		
		with result_expander:
			col4, col5 = st.beta_columns((3,2))			


		if run_triggered and response.status_code == 200:	

			json_data = json.loads(response.text)
			st.success('Forecast Successful, Response code:'+str(response.status_code))

			delivery_df = pd.DataFrame(data={'timestamp':json_data['delivery_timestamp'],
											 'delivered_units':json_data['delivery_units']
											})					
			delivery_df['timestamp'] = pd.to_datetime(delivery_df['timestamp'])
											
			forecast_df = pd.DataFrame(data={'timestamp': json_data['forecast_timestamp'],
											 'predicted_demand_units': json_data['predicted_demand_units'],
											 'optimised_demand_units': json_data['optimised_demand_units'],
											})													
			forecast_df['timestamp'] = pd.to_datetime(forecast_df['timestamp'])													

			fig_output = go.Figure()
			fig_output.update_layout(title="Forecast Demand")

			fig_output.add_trace(
				go.Bar(x=forecast_df['timestamp'], 
					   y=forecast_df['predicted_demand_units'],
					   name="Forecasted Demand"))


			fig_output.add_trace(
				go.Bar(x=delivery_df['timestamp'], 
					   y=delivery_df['delivered_units'],
					   name="Optimised Replenishments"))

			fig_output.update_layout(legend=dict(
				orientation="h",
				yanchor="bottom",
				y=1.02,
				xanchor="right",
				x=1
			))

			st.plotly_chart(fig_output, use_container_width=True)

			merged_df = pd.merge(delivery_df, forecast_df, on = 'timestamp', how='outer').fillna(0).sort_values('timestamp', ascending=True)

			st.dataframe(merged_df)
			csv = merged_df.to_csv(index=False)
			b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
			href = f'<a href="data:file/csv;base64,{b64}" download="replenishment.csv">Download Results in CSV format</a>'
			st.markdown(href, unsafe_allow_html=True)				

		elif run_triggered and response.status_code != 200:	
			error = 'Backcast Failed, Response code:'+str(response.status_code)+', Error message:'+response.text
			st.exception(error)
			
		else:
			st.write('Forecast has not yet been run')							

		
	elif choice == "Backcast":
	
		st.title("Backcast")
		
		input_data_expander = st.beta_expander("Historical Demand Data", expanded=True)		
		
		with input_data_expander:
			file_upload_selector = ["Use Example File","Upload A File"]
# 			upload_file_choice = st.sidebar.selectbox("Time Series Data", file_upload_selector)

			col1, col2 = st.beta_columns(2)
			
			with col1:
				upload_file_choice = st.selectbox("Time Series Data", file_upload_selector)
			
				if upload_file_choice == "Use Example File":
					data_file = 'https://raw.githubusercontent.com/bluedotthinking/wastenot-documentation/master/example_data/bdt_example_input.csv'
					input_df = pd.read_csv(data_file)
					st.write('The example file contains historical demand data with 2 columns:')
					st.write('- "date", containing dates in the format YYYY-MM-DD')			
					st.write('- "demand_units", containing only integers (whole numbers)')									
					
# 					fig_input = go.Figure()
# 					fig_input.update_layout(title="Historical Demand Data")
# 					fig_input.add_trace(
# 						go.Bar(x=input_df['date'].values, y=input_df['demand_units'].values,
# 							   name="Training Data"))
# 					st.plotly_chart(fig_input, use_container_width=True)
# 					st.dataframe(input_df)

				if upload_file_choice == "Upload A File":
	# 				data_file = st.sidebar.file_uploader("Upload CSV",type=['csv'])
					data_file = None
					data_file = st.file_uploader("Upload CSV",type=['csv'])
					st.write('The file you upload with historical demand data must have 2 columns:')
					st.write('- "date", containing dates in the format YYYY-MM-DD')			
					st.write('- "demand_units", containing only integers (whole numbers)')										

			with col2:
			
				if data_file is not None:
# 					file_details = {"Filename":data_file.name,"FileType":data_file.type,"FileSize":data_file.size}
					input_df = pd.read_csv(data_file)
				
					fig_input = go.Figure()
					fig_input.update_layout()
					fig_input.add_trace(
						go.Bar(x=input_df['date'].values, y=input_df['demand_units'].values,
							   name="Training Data"))
					st.plotly_chart(fig_input, use_container_width=True)
# 					st.dataframe(input_df)

				else:
					st.write('Please upload some data')

		st.markdown('#')		

		simulation_params_expander = st.beta_expander("Simulation Parameters", expanded=False)
		with simulation_params_expander:
			opt_param, unit_cost, unit_sell_price, currency_symbol, forecast_ahead_periods, shelf_life_days, shelf_life_seconds, fraction_wasted, replenishment_daysofweek, n_forecasts_simulated, n_training_periods= set_simulation_params(choice)
		st.markdown('#')			


		n_periods_simulated = int(forecast_ahead_periods*n_forecasts_simulated)

		run_triggered = False					
		col3, col4 = st.beta_columns((1,3))
		
		with col4:
			if access_token == '':
				st.write('Get your Access Token at https://www.bluedotthinking.com/subscriptions/')
			else:		
				st.write('Perform a backcast with the provided file, with a unit cost of',
							currency_symbol,unit_cost,', unit sell-price of',currency_symbol,unit_sell_price,', and a shelf-life of',shelf_life_days,'days.  Carrying out,',n_forecasts_simulated,'forecasts, forecasting',forecast_ahead_periods,'periods (days) ahead each time')
				st.write('The first',n_training_periods,'periods (days) will be used as the training data, and the following',
							n_periods_simulated,'periods will be simulated')
		with col3:
			if st.button("Run Backcast"):


				response = backcast_request(access_token, input_df, unit_sell_price, unit_cost, shelf_life_seconds, 
									 opt_param, forecast_ahead_periods, replenishment_daysofweek, n_training_periods, n_forecasts_simulated,
									 fraction_wasted)
				json_data = json.loads(response.text)
				
				run_triggered = True


		if run_triggered and response.status_code == 200:
# 		if response:
			st.header('Results')
			st.write('Backcast Successful, Response code:',response.status_code)			

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
			results_df['fraction_of_demand_satisfied'] = results_df['simulation_satisfied_units'] / results_df['actual_demand_units_unconstrained']

			calculate_benefits(results_df, json_data, fraction_wasted, unit_sell_price, unit_cost, currency_symbol)
		elif run_triggered and response.status_code != 200:	
			error = 'Backcast Failed, Response code:'+str(response.status_code)+', Error message:'+response.text

			st.exception(error)
			

if __name__ == '__main__':
	main()
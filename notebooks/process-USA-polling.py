# This script generates the data to be loaded by usa-presidential-poll.ipynb
import geopandas as gpd 
import pandas as pd

# Here we load two data files, the first is a geometry dataset for the USA by states
# and the second is polling for candidates in the 2020 presendential election, also by states.
geo_states = gpd.read_file('gz_2010_us_040_00_500k.json')
df_polls = pd.read_csv('presidential_poll_averages_2020.csv')

# Filter our poll data to remove third party candidates:
trump_biden_data = df_polls[
    df_polls['candidate_name'].isin(['Donald Trump', 'Joseph R. Biden Jr.'])
]

# Our spatial and poll data have the name of the state in common.
# We will change the name of the state to NAME to match our geospatial dataframe.
trump_biden_data.columns = ['cycle', 'NAME', 'modeldate', 'candidate_name', 'pct_estimate', 'pct_trend_adjusted']

# We can join the geospatial and poll data using the NAME column (the name of the state).
geo_states_trump_biden = geo_states.merge(trump_biden_data, on='NAME')

# Save the csv for easy loading by the notebook
geo_states_trump_biden.to_csv('geo_states_trump_biden.csv')


import streamlit as st
import pandas as pd
import altair as alt

# %% Collect Data 

#### Provincial Case Counts
prov_cases_df = pd.read_csv('https://raw.githubusercontent.com/dsfsi/covid19za/master/data/covid19za_provincial_cumulative_timeline_confirmed.csv')

#### Provincial Death Counts
prov_deaths_df = pd.read_csv('https://raw.githubusercontent.com/dsfsi/covid19za/master/data/covid19za_provincial_cumulative_timeline_deaths.csv')

# %% Provincial Data Frame


prov_cases_df = prov_cases_df[['date', 'YYYYMMDD', 'EC', 'FS','GP','KZN','LP','MP','NC','NW','WC','UNKNOWN']]
prov_cases_df.columns = ['Date','YYYYMMDD','Eastern Cape','Free State','Gauteng','KwaZulu-Natal','Limpopo','Mpumalanga','Northern Cape','North West','Western Cape','UNKNOWN']

prov_deaths_df = prov_deaths_df[['date', 'YYYYMMDD', 'EC', 'FS','GP','KZN','LP','MP','NC','NW','WC','UNKNOWN']]
prov_deaths_df.columns = ['Date','YYYYMMDD','Eastern Cape','Free State','Gauteng','KwaZulu-Natal','Limpopo','Mpumalanga','Northern Cape','North West','Western Cape','UNKNOWN']


prov_cases_df = prov_cases_df.melt(id_vars=["Date","YYYYMMDD"], 
                                var_name="Province", 
                                value_name="Cases")

prov_cases_df['Prev Cases'] = (prov_cases_df.sort_values(by=['YYYYMMDD'], ascending=True)
                      .groupby(['Province'])['Cases'].shift(1))


prov_deaths_df = prov_deaths_df.melt(id_vars=["Date","YYYYMMDD"], 
                                var_name="Province", 
                                value_name="Deaths")

prov_data_df = pd.merge(prov_cases_df, prov_deaths_df[['YYYYMMDD', 'Province', 'Deaths']],
                       how='left', on=['YYYYMMDD', 'Province'])

prov_data_df['Prev Deaths'] = (prov_data_df.sort_values(by=['YYYYMMDD'], ascending=True)
                      .groupby(['Province'])['Deaths'].shift(1))

prov_data_df['YYYYMMDD'] = prov_data_df['YYYYMMDD'].apply(str)

prov_data_df['Date'] =  pd.to_datetime(prov_data_df['Date'], format='%d-%m-%Y')


prov_data_df['NewCases']=prov_data_df['Cases'] - prov_data_df['Prev Cases']
prov_data_df['NewDeaths']=prov_data_df['Deaths'] - prov_data_df['Prev Deaths']


#prov_data_df.info()

# %% Provincial App initials

st.title("COVID-19 SOUTH AFRICA ")

var=prov_data_df['Date'].max().strftime('%Y-%m-%d')
st.markdown('Data Last Updated: ' +str(var))

#### Time Sider
firstdate =prov_data_df['Date'].min()
enddate   =prov_data_df['Date'].max()

st.header('1. Select The Date Range:')
start_date = st.date_input('Start date', firstdate)
end_date = st.date_input('End date', enddate)


start_date = start_date.strftime('%Y-%m-%d')
end_date = end_date.strftime('%Y-%m-%d')

#### Provincial selector 
st.header('2. Select The Province:')

defaultcols = ['Eastern Cape', 'Free State', 'Gauteng', 'KwaZulu-Natal',
       'Limpopo', 'Mpumalanga', 'Northern Cape', 'North West',
       'Western Cape', 'UNKNOWN']

option = st.multiselect( 'Which Province do you want to see?', options=defaultcols , default=defaultcols)

# %% Graphs


dff=prov_data_df[(prov_data_df['Date'] >= start_date) & (prov_data_df['Date']<=end_date) & (prov_data_df['Province'].isin(option))]   

st.header('3. View Graphs')

#### 1
chart=alt.Chart(dff,title=f"New Daily Covid-19 Cases By Province").mark_bar().encode(
    x='YYYYMMDD',
    y='sum(NewCases)',
    color='Province'
    )

chart = chart.configure_title(fontSize=20, offset=5, orient='top', anchor='middle')

chart

#### 2
chart=alt.Chart(dff,title=f"New Daily Covid-19 Deaths By Province").mark_bar().encode(
    x='YYYYMMDD',
    y='sum(NewDeaths)',
    color='Province'
    )

chart = chart.configure_title(fontSize=20, offset=5, orient='top', anchor='middle')

chart

#### 3
chart=alt.Chart(dff,title=f"Cumulative Cases").mark_line().encode(
    x='YYYYMMDD',
    y='Cases',
    color='Province'
)

chart = chart.configure_title(fontSize=20, offset=5, orient='top', anchor='middle')

chart 


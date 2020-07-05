

import streamlit as st
import pandas as pd
import altair as alt

# %% Collect Data 

#### Provincial Case Cuml Counts
prov_cases_df = pd.read_csv('https://raw.githubusercontent.com/dsfsi/covid19za/master/data/covid19za_provincial_cumulative_timeline_confirmed.csv')

#### Provincial Death Cuml Counts
prov_deaths_df = pd.read_csv('https://raw.githubusercontent.com/dsfsi/covid19za/master/data/covid19za_provincial_cumulative_timeline_deaths.csv')

#### Provincial Recovery Cuml Counts
prov_recoveries_df = pd.read_csv('https://raw.githubusercontent.com/dsfsi/covid19za/master/data/covid19za_provincial_cumulative_timeline_recoveries.csv')

prov_recoveries_df.info()

# %% Provincial Data Frame


prov_cases_df = prov_cases_df[['date', 'YYYYMMDD', 'EC', 'FS','GP','KZN','LP','MP','NC','NW','WC','UNKNOWN']]
prov_cases_df.columns = ['Date','YYYYMMDD','Eastern Cape','Free State','Gauteng','KwaZulu-Natal','Limpopo','Mpumalanga','Northern Cape','North West','Western Cape','UNKNOWN']

prov_deaths_df = prov_deaths_df[['date', 'YYYYMMDD', 'EC', 'FS','GP','KZN','LP','MP','NC','NW','WC','UNKNOWN']]
prov_deaths_df.columns = ['Date','YYYYMMDD','Eastern Cape','Free State','Gauteng','KwaZulu-Natal','Limpopo','Mpumalanga','Northern Cape','North West','Western Cape','UNKNOWN']

prov_recoveries_df = prov_recoveries_df[['date', 'YYYYMMDD', 'EC', 'FS','GP','KZN','LP','MP','NC','NW','WC','UNKNOWN']]
prov_recoveries_df.columns = ['Date','YYYYMMDD','Eastern Cape','Free State','Gauteng','KwaZulu-Natal','Limpopo','Mpumalanga','Northern Cape','North West','Western Cape','UNKNOWN']


prov_cases_df = prov_cases_df.melt(id_vars=["Date","YYYYMMDD"], 
                                var_name="Province", 
                                value_name="Cases")

prov_cases_df['Prev Cases'] = (prov_cases_df.sort_values(by=['YYYYMMDD'], ascending=True)
                      .groupby(['Province'])['Cases'].shift(1))


prov_deaths_df = prov_deaths_df.melt(id_vars=["Date","YYYYMMDD"], 
                                var_name="Province", 
                                value_name="Deaths")

prov_recoveries_df = prov_recoveries_df.melt(id_vars=["Date","YYYYMMDD"], 
                                var_name="Province", 
                                value_name="Recoveries")

prov_data_df = pd.merge(prov_cases_df, prov_deaths_df[['YYYYMMDD', 'Province', 'Deaths']],
                       how='left', on=['YYYYMMDD', 'Province'])

prov_data_df = pd.merge(prov_data_df , prov_recoveries_df[['YYYYMMDD', 'Province', 'Recoveries']],
                       how='left', on=['YYYYMMDD', 'Province'])



prov_data_df['Prev Deaths'] = (prov_data_df.sort_values(by=['YYYYMMDD'], ascending=True)
                      .groupby(['Province'])['Deaths'].shift(1))

prov_data_df['YYYYMMDD'] = prov_data_df['YYYYMMDD'].apply(str)

prov_data_df['Date'] =  pd.to_datetime(prov_data_df['Date'], format='%d-%m-%Y')


prov_data_df['NewCases']=prov_data_df['Cases'] - prov_data_df['Prev Cases']
prov_data_df['NewDeaths']=prov_data_df['Deaths'] - prov_data_df['Prev Deaths']
prov_data_df['Active']=prov_data_df['Cases'] - prov_data_df['Deaths'] - prov_data_df['Recoveries']


### Custom data set 

cum_df_d= prov_data_df[['Date','YYYYMMDD','Province','Deaths']]
cum_df_a = prov_data_df[['Date','YYYYMMDD','Province','Active']]
cum_df_r = prov_data_df[['Date','YYYYMMDD','Province','Recoveries']]

cum_df_d['x'] = 1
cum_df_a['x'] = 2
cum_df_r['x'] = 3

cum_df_d.columns = ['Date','YYYYMMDD','Province','Value','Phase']
cum_df_a.columns = ['Date','YYYYMMDD','Province','Value','Phase']
cum_df_r.columns = ['Date','YYYYMMDD','Province','Value','Phase']


df_union_all= pd.concat([cum_df_d,cum_df_a ,cum_df_r])
df_union_all['Phase'] = df_union_all['Phase'].map({1:'Deaths', 2:'Active',3:'Recovered'})



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
df_union_all=df_union_all[(df_union_all['Date'] >= start_date) & (df_union_all['Date']<=end_date) & (df_union_all['Province'].isin(option))] 

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

#### 4

chart=alt.Chart(dff,title=f"Active Cases").mark_line().encode(
    x='YYYYMMDD',
    y='Active',
    color='Province'
)

chart = chart.configure_title(fontSize=20, offset=5, orient='top', anchor='middle')

chart 

#### 5

chart=alt.Chart(dff,title=f"New Cases Trellis Chart").mark_bar().encode(
    x='YYYYMMDD',
    y='sum(NewCases)',
    color="Province:N",
    row='Province'
).properties(
    height=100
)

chart = chart.configure_title(fontSize=20, offset=5, orient='top', anchor='middle')

chart 

#### 6

chart=alt.Chart(df_union_all,title=f"Cumulative Cases State").mark_area().encode(
    x='YYYYMMDD',
    y='sum(Value)',
    color='Phase'
)

chart = chart.configure_title(fontSize=20, offset=5, orient='top', anchor='middle')

chart

#### 5

chart=alt.Chart(df_union_all,title=f"Cases Stage Trellis Chart").mark_bar().encode(
    x='YYYYMMDD',
    y='sum(Value)',
    color="Phase:N",
    row='Phase'
).properties(
    height=100
)

chart = chart.configure_title(fontSize=20, offset=5, orient='top', anchor='middle')

chart 

###
# dff=df_union_all[(df_union_all['Date']==end_date) & (df_union_all['Province'].isin(option))] 
# st.table(dff)


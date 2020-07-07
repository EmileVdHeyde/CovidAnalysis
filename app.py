

import streamlit as st
import pandas as pd
import altair as alt
from datetime import date, timedelta

pd.options.display.max_columns = None
pd.options.display.max_rows = 500

# %% Collect Data 

#### Provincial Case Cuml Counts
prov_cases_df = pd.read_csv('https://raw.githubusercontent.com/dsfsi/covid19za/master/data/covid19za_provincial_cumulative_timeline_confirmed.csv')

#### Provincial Death Cuml Counts
prov_deaths_df = pd.read_csv('https://raw.githubusercontent.com/dsfsi/covid19za/master/data/covid19za_provincial_cumulative_timeline_deaths.csv')

#### Provincial Recovery Cuml Counts
prov_recoveries_df = pd.read_csv('https://raw.githubusercontent.com/dsfsi/covid19za/master/data/covid19za_provincial_cumulative_timeline_recoveries.csv')



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


### Custom data set for cumulative chart 

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

###########  Table Data

latestdate=prov_data_df['Date'].max().strftime('%Y-%m-%d')

dfc=prov_data_df[(prov_data_df['Date']==latestdate)]

#population 
population=[['Eastern Cape', 6712276] ,
      ['Free State',  2887465] ,
      ['Gauteng', 15176115] ,
      ['KwaZulu-Natal', 11289086] ,
      ['Limpopo', 5982584 ] ,
      ['Mpumalanga', 4592187 ] ,
      ['Northern Cape',4027160 ] , 
      ['North West', 1263875 ] ,
      ['Western Cape', 6844272]]

dfp = pd.DataFrame(population, columns = ['Province', 'Population'])

dfs= pd.merge(dfc, dfp,
                       how='left', on=['Province'])

dfs=dfs.set_index('Province')

#total  
#prov_data_df.loc[:,'South Africa'] = prov_data_df.sum(numeric_only=True, axis=1)
dfs.loc['South Africa']= dfs.sum(numeric_only=True, axis=0)


#rates calculation
dfs['RecoveryRate']=dfs['Recoveries']/dfs['Cases']
dfs['FatalityRate']=dfs['Deaths']/dfs['Cases']
dfs['CasesPerHundredThousand'] = 100000*(dfs['Cases']/dfs['Population'])
dfs['DeathsPerHundredThousand'] = 100000*(dfs['Deaths']/dfs['Population'])
dfs['NewCasesPerHundredThousand'] = 100000*(dfs['NewCases']/dfs['Population'])
#dfs

#clean up 
dfs.drop(['Date', 'YYYYMMDD','Prev Cases','Prev Deaths'], axis=1, inplace=True)
dfs = dfs.drop('UNKNOWN')
#dfs


dfs1 = dfs[['Cases','Active','Deaths','Recoveries','RecoveryRate','FatalityRate']]
dfs2 = dfs[['NewCases','NewDeaths']]
dfs3 = dfs[['CasesPerHundredThousand','DeathsPerHundredThousand','NewCasesPerHundredThousand']]


dfs1=dfs1.style.format({
    'RecoveryRate': '{:,.1%}'.format,
    'FatalityRate': '{:,.1%}'.format,
    'Cases': '{:,.0f}'.format,
    'Active': '{:,.0f}'.format,
    'Deaths': '{:,.0f}'.format,
    'Recoveries': '{:,.0f}'.format
  })

dfs2=dfs2.style.format({
    'NewCases': '{:,.0f}'.format,
    'NewDeaths': '{:,.0f}'.format
  })


dfs3=dfs3.style.format({
    'CasesPerHundredThousand': '{:,.0f}'.format,
    'DeathsPerHundredThousand': '{:,.1f}'.format,
    'NewCasesPerHundredThousand': '{:,.0f}'.format
  })



# %% Provincial App initials

st.title("COVID-19 SOUTH AFRICA ")


st.markdown('Data Last Updated: ' +str(latestdate))

#### Time Sider
#firstdate =prov_data_df['Date'].min()
enddate   =prov_data_df['Date'].max()
firstdate= enddate - timedelta(30)

#print(defaultstart)

st.header('1. Select The Date Range:')
start_date = st.date_input('Start date', firstdate)
end_date = st.date_input('End date', enddate)


start_date = start_date.strftime('%Y-%m-%d')
end_date = end_date.strftime('%Y-%m-%d')

#### Provincial selector 
st.header('2. Select The Province:')

defaultcols = ['Eastern Cape', 'Free State', 'Gauteng', 'KwaZulu-Natal',
       'Limpopo', 'Mpumalanga', 'Northern Cape', 'North West',
       'Western Cape']

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
).properties(width=800, height=500)

chart = chart.configure_title(fontSize=20, offset=5, orient='top', anchor='middle')

chart 

#### 2
chart=alt.Chart(dff,title=f"New Daily Covid-19 Deaths By Province").mark_bar().encode(
    x='YYYYMMDD',
    y='sum(NewDeaths)',
    color='Province'
    ).properties(width=800, height=500)

chart = chart.configure_title(fontSize=20, offset=5, orient='top', anchor='middle')

chart

#### 3
chart=alt.Chart(dff,title=f"Cumulative Cases").mark_line().encode(
    x='YYYYMMDD',
    y='Cases',
    color='Province'
).properties(width=800, height=500)

chart = chart.configure_title(fontSize=20, offset=5, orient='top', anchor='middle')

chart 

#### 4

chart=alt.Chart(dff,title=f"Active Cases").mark_line().encode(
    x='YYYYMMDD',
    y='Active',
    color='Province'
).properties(width=800, height=500)

chart = chart.configure_title(fontSize=20, offset=5, orient='top', anchor='middle')

chart 

#### 5

chart=alt.Chart(dff,title=f"New Cases Trellis Chart").mark_bar().encode(
    x='YYYYMMDD',
    y='sum(NewCases)',
    color="Province:N",
    row='Province'
).properties(width=500, height=250
).resolve_scale(
    y='independent'
)

chart = chart.configure_title(fontSize=20, offset=5, orient='top', anchor='middle')

chart 

#### 6

chart=alt.Chart(df_union_all,title=f"Cumulative Cases by Phase").mark_area().encode(
    x='YYYYMMDD',
    y='sum(Value)',
    color='Phase'
).properties(width=800, height=500)

chart = chart.configure_title(fontSize=20, offset=5, orient='top', anchor='middle')

chart

#### 5

st.header('4. Current View:')
# st.dataframe(dfs1,width=900 , height=750)
# st.dataframe(dfs2,width=900 , height=750)
# st.dataframe(dfs3,width=900 , height=800)

st.text('Table 1: Current Cumulative Cases')
st.table(dfs1)

st.text('Table 2: Current New Cases and Deaths')
st.table(dfs2)

st.text('Table 3: Current Population Scaled Measures')
st.table(dfs3)

st.markdown('Data Source: Data Science for Social Impact research group, led by Dr. Vukosi Marivate, at the University of Pretoria')
st.markdown('Population Data Source: Stats SA 2019 mid-year estimate')






# chart=alt.Chart(df_union_all,title=f"Cases Phase Trellis Chart").mark_bar().encode(
#     x='YYYYMMDD',
#     y='sum(Value)',
#     color="Phase:N",
#     row='Phase'
# ).properties(
#     height=100
# ).resolve_scale(
#     y='independent'
# )
    
# chart = chart.configure_title(fontSize=20, offset=5, orient='top', anchor='middle')

# chart 

###
# 

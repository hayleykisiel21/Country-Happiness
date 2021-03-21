#!/usr/bin/env python
# coding: utf-8

# # CS 5010
#  
# # Semester Project 
#  
# # Happiness Data Set
#  
# # Team GH2JM:
# 
# # Haley Blair, Melanie Sattler, Jen Leopold, Hayley Kisiel, & George White 
# 

# ## Importing necessary packages: 

# In[2]:


import pandas as pd
import plotly.express as px  # (version 4.7.0) pip install plotly
import plotly.graph_objects as go
import dash  # (version 1.12.0) pip install dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pycountry
from jupyter_dash import JupyterDash
import plotly.io as pio


# ## Data setup: 

# ### Saving files for each year as separate dataframes 

# In[22]:


df_2015 = pd.read_csv ('2015.csv',                        usecols= ['Country','Region','Happiness Rank','Happiness Score'])
df_2016 = pd.read_csv ('2016.csv',                        usecols= ['Country','Happiness Rank', 'Happiness Score'])
df_2017 = pd.read_csv ('2017.csv',                        usecols= ['Country','Happiness.Rank', 'Happiness.Score','Family','Dystopia.Residual'])
df_2018 = pd.read_csv ('2018.csv',                        usecols= ['Overall rank','Country or region','Score'])
df_2019 = pd.read_csv ('2019.csv',                        usecols= ['Overall rank','Country or region','Score',                        'GDP per capita','Social support','Healthy life expectancy',                        'Freedom to make life choices','Generosity','Perceptions of corruption'])


# ### Creating one dataframe from all the separate files for different years 

# In[4]:


df = df_2015.merge(df_2016, on='Country')
df = df.merge(df_2017, on='Country')
df = df.merge(df_2018, left_on='Country', right_on='Country or region')
df = df.merge(df_2019, on='Country or region')


# ### Renaming and rearranging the columns of the dataframe to make logical sense 

# In[5]:


df.rename(columns={'Happiness Rank_x': 'Rank 2015','Happiness Score_x': 'Happiness Score 2015',    'Happiness Rank_y': 'Rank 2016','Happiness Score_y': 'Happiness Score 2016',    'Happiness.Rank': 'Rank 2017','Happiness.Score': 'Happiness Score 2017',    'Dystopia.Residual': 'Dystopia Residual','Overall rank_x': 'Rank 2018',    'Score_x': 'Happiness Score 2018','Overall rank_y': 'Rank 2019',    'Score_y': 'Happiness Score 2019'}, inplace=True)
    
# rearrange columns
df = df[['Country','Region','Happiness Score 2015','Happiness Score 2016',        'Happiness Score 2017','Happiness Score 2018','Happiness Score 2019','Rank 2015','Rank 2016'        ,'Rank 2017','Rank 2018','Rank 2019','Family','GDP per capita','Social support',        'Healthy life expectancy','Freedom to make life choices','Generosity',        'Perceptions of corruption','Dystopia Residual']]


# ### Top 10 Happiness scores for 2019 

# In[6]:


print(df.nsmallest(10,['Rank 2019'])) 


# ### Lowest 10 Happiness scores for 2019 

# In[7]:


print(df.nlargest(10,['Rank 2019']))


# ## Creating a map to visualize happiness around the world: 

# ### Intialize app

# In[8]:


app = JupyterDash(__name__)


# ### Use groupby to eliminate uneccesary columns and structure dataset

# In[9]:


df1 = df.groupby(['Country', 'Region'])[['Happiness Score 2015','Happiness Score 2016','Happiness Score 2017',
                 'Happiness Score 2018','Happiness Score 2019']].mean() # eliminated unnecessary columns
df1.reset_index(inplace=True)


# ### Renaming countries by official names to add ISO codes 

# In[10]:


df1 = df1.replace(to_replace = 'Bolivia', value = 'Bolivia, Plurinational State of')
df1 = df1.replace(to_replace = 'Congo (Brazzaville)', value = 'Congo')
df1 = df1.replace(to_replace = 'Czech Republic', value = 'Czechia')
df1 = df1.replace(to_replace = 'Iran', value = 'Iran, Islamic Republic of')
df1 = df1.replace(to_replace = 'Ivory Coast', value = "Côte d'Ivoire")
df1 = df1.replace(to_replace = 'Moldova', value = 'Moldova, Republic of')
df1 = df1.replace(to_replace = 'Palestinian Territories', value = 'Palestine, State of')
df1 = df1.replace(to_replace = 'Russia', value = 'Russian Federation')
df1 = df1.replace(to_replace = 'South Korea', value = 'Korea, Republic of')
df1 = df1.replace(to_replace = 'Syria', value =  'Syrian Arab Republic')
df1 = df1.replace(to_replace = 'Tanzania', value = 'Tanzania, United Republic of')
df1 = df1.replace(to_replace = 'Venezuela', value = 'Venezuela, Bolivarian Republic of')
df1 = df1.replace(to_replace = 'Vietnam', value = 'Viet Nam')


# ### Creating a dictionary for countries and ISO3 codes 

# In[11]:


input_countries = df1['Country']

countries = {}
for country in pycountry.countries:
    countries[country.name] = country.alpha_3 


# ### Create a new column in the dataframe for ISO3 codes

# In[12]:


df1['ISO3'] = [countries.get(country, 'Unknown code') for country in input_countries]
df1 = df1.drop([29,67],axis=0) # removing countries that no longer exist


# ### Creating app layout

# In[13]:


app.layout = html.Div([
    html.H1("World Happiness",style={'text-align':'center'}),
    dcc.Slider(
    id='my_slider',
    min=2015,
    max=2019,
    step=1,
    value=2015),
    html.Div(id='slider_output_container',children={}),
    html.Br(),
    dcc.Graph(id="my_happy_map",figure={})
])


# ### Defining the inputs and outputs using callback and creating the actual figure 

# In[14]:


@app.callback(
    [Output(component_id='slider_output_container', component_property='children'),
     Output(component_id='my_happy_map',component_property='figure')],
    [dash.dependencies.Input('my_slider', 'value')]
)
def update_graph(option_slctd):
    print(option_slctd)
    print(type(option_slctd))
    
    # prints which year the person chose 
    container = "The year chosen by user was: {}".format(option_slctd)
    dff = df1.copy() # creates a copy of dataframe for use
    # defines the happiness score for each for graphing
    if option_slctd == 2015:
        dff = dff[["Country","Region",'ISO3',"Happiness Score 2015"]]
        dff = dff.rename(columns={"Happiness Score 2015": 'Happiness Score'})
    elif option_slctd == 2016:
        dff = dff[["Country","Region",'ISO3',"Happiness Score 2016"]]
        dff = dff.rename(columns={"Happiness Score 2016": 'Happiness Score'})
    elif option_slctd == 2017:
        dff = dff[['Country','Region','ISO3','Happiness Score 2017']]
        dff = dff.rename(columns={"Happiness Score 2017": 'Happiness Score'})
    elif option_slctd == 2018:
        dff = dff[['Country','Region','ISO3','Happiness Score 2018']]
        dff = dff.rename(columns={"Happiness Score 2018": 'Happiness Score'})
    else:
        dff = dff[['Country','Region','ISO3','Happiness Score 2019']]
        dff = dff.rename(columns={"Happiness Score 2019": 'Happiness Score'})
    # Plotly Express to show a map of the world with colored regions for the happiness score
    fig = px.choropleth(
        data_frame=dff,
        locations=dff["ISO3"],
        color=dff['Happiness Score'],
        hover_data=dff[['Country', 'Happiness Score']],
        color_continuous_scale=px.colors.sequential.Plasma
        )
    
    return container, fig


# ### Prints the map figure 

# In[15]:


app.run_server(mode='inline')


# ## Investigating the top 5 and bottom 5 happiness scores 

# ### Creates a Dataframe that pulls the Top 10 Happiest Countries based on the 2015 Rank
# ### Originally wanted to use this to look at the happiness score, but it didn't work 
# ### Saving the code now in case useful somewhere else

# In[16]:


Top102015List=(df[(df['Rank 2015'] <11) & (df['Happiness Score 2015'] > 5)][['Country']])
print("Top 10 countries in 2015 Rank")
print(Top102015List)


# ### Creating dataframes with only top/bottom 5 for each year

# In[17]:


#Creating a data frame with only the the top 5 for 2015 ranking
Top5_2015=df[:5]
print(Top5_2015)

#Creating a Dataframe with only the bottom 5 for 2015 ranking
Bottom5_2015= df[-5:]
print(Bottom5_2015)

#Creating Dataframe for top 5 coutnries for 2016 ranking
Top5_2016 = df[df['Rank 2016'] <=5]
print(Top5_2016)

#Creating Dataframe for bottom 5 coutnries for 2016 ranking
Bottom5_2016 = df[df['Rank 2016'] >152]
print(Bottom5_2016)

#Creating Dataframe for top 5 coutnries for 2017 ranking
Top5_2017 = df[df['Rank 2017'] <=5]
print(Top5_2017)

#Creating Dataframe for bottom 5 coutnries for 2017 ranking
Bottom5_2017 = df[df['Rank 2017'] >149]
print(Bottom5_2017)

#Creating Dataframe for top 5 coutnries for 2018 ranking
Top5_2018 = df[df['Rank 2018'] <=5]
print(Top5_2018)

#Creating Dataframe for bottom 5 coutnries for 2018 ranking
Bottom5_2018 = df[df['Rank 2018'] >149]
print(Bottom5_2018)

#Creating Dataframe for top 5 coutnries for 2019 ranking
Top5_2019 = df[df['Rank 2019'] <=5]
print(Top5_2019)

#Creating Dataframe for bottom 5 coutnries for 2019 ranking
Bottom5_2019 = df[df['Rank 2019'] >149]
print(Bottom5_2019)


# ### Calculating the avergae GDP for the top/bottom 5 for each year

# In[18]:


#Calculating the Average GDP for the 2015 Top 5
Mean_Top_2015=Top5_2015["GDP per capita"].mean()
print("The Average GDP for the Top 5 Countries in 2015")
print(Mean_Top_2015)

#Calculating the Average GDP for the 2016 Top 5
Mean_Top_2016=Top5_2016["GDP per capita"].mean()
print("The Average GDP for the Top 5 Countries in 2016")
print(Mean_Top_2016)

#Calculating the Average GDP for the 2017 Top 5
Mean_Top_2017=Top5_2017["GDP per capita"].mean()
print("The Average GDP for the Top 5 Countries in 2017")
print(Mean_Top_2017)

#Calculating the Average GDP for the 2018 Top 5
Mean_Top_2018=Top5_2018["GDP per capita"].mean()
print("The Average GDP for the Top 5 Countries in 2018")
print(Mean_Top_2018)

#Calculating the Average GDP for the 2019 Top 5
Mean_Top_2019=Top5_2019["GDP per capita"].mean()
print("The Average GDP for the Top 5 Countries in 2019")
print(Mean_Top_2019)

#Calculating the Average GDP for the 2015 Bottom 5
Mean_Bottom_2015=Bottom5_2015["GDP per capita"].mean()
print("The Average GDP for the Bottom 5 Countries in 2015")
print(Mean_Bottom_2015)

#Calculating the Average GDP for the 2016 Bottom 5
Mean_Bottom_2016=Bottom5_2016["GDP per capita"].mean()
print("The Average GDP for the Bottom 5 Countries in 2016")
print(Mean_Bottom_2016)

#Calculating the Average GDP for the 2017 Bottom 5
Mean_Bottom_2017=Bottom5_2017["GDP per capita"].mean()
print("The Average GDP for the Bottom 5 Countries in 2017")
print(Mean_Bottom_2017)

#Calculating the Average GDP for the 2018 Bottom 5
Mean_Bottom_2018=Bottom5_2018["GDP per capita"].mean()
print("The Average GDP for the Bottom 5 Countries in 2018")
print(Mean_Bottom_2018)

#Calculating the Average GDP for the 2019 Bottom 5
Mean_Bottom_2019=Bottom5_2019["GDP per capita"].mean()
print("The Average GDP for the Bottom 5 Countries in 2019")
print(Mean_Bottom_2019)


# ### Calculating the average GDP for the top/bottom 5 over all 5 years

# In[19]:


Top_Country_Average=(Mean_Top_2015+Mean_Top_2016+Mean_Top_2017+Mean_Top_2018+Mean_Top_2019)/5
Bottom_Country_Average=(Mean_Bottom_2015+Mean_Bottom_2016+Mean_Bottom_2017+Mean_Bottom_2018+Mean_Bottom_2019)/5

print("Average GDP for the Top 5 Countries over the 5 years",Top_Country_Average)
print("Average GDP for the Bottom 5 Countries over the 5 years",Bottom_Country_Average)


# ## Looking at the top 5 happiest countries for 2015

# In[23]:


happy_df = pd.read_csv ('2015.csv')
data_top1=happy_df.head()
data_top1


# ## Creating a bar graph for Happiness Scores by Country in 2015

# In[25]:


fig= px.bar(happy_df, x='Country', y='Happiness Score', color='Country', title ='Happiness Score 2015', color_discrete_sequence=["olive", "olivedrab","orange", "powderblue", "chartreuse", "chocolate"])
fig.update_xaxes(type='category')
fig.update_xaxes(automargin=True)
fig.update_yaxes(automargin=True)
fig.show("png")


# ## Creating a 3D plot of Trust vs. Family vs. Happiness Score in 2015

# In[26]:


fig = px.scatter_3d(
    data_frame=happy_df,
    x='Trust (Government Corruption)',
    y='Family',
    z='Happiness Score',
    color="Region",
    color_discrete_sequence= px.colors.qualitative.Vivid,
    log_x=True,  # you can also set log_y and log_z as a log scale
    # range_z=[9,13],           # you can also set range of range_y and range_x
    template='plotly_dark',         # 'ggplot2', 'seaborn', 'simple_white', 'plotly',
                                # 'plotly_white', 'plotly_dark', 'presentation',
                                # 'xgridoff', 'ygridoff', 'gridon', 'none'
    title='Happiness Test Graph',
    labels={'Economy': 'Region'},
    hover_name='Country',        # values appear in bold in the hover tooltip
    height=2000                 # height of graph in pixels

)

fig.write_html("Sample3Dplot.html")
pio.show(fig)


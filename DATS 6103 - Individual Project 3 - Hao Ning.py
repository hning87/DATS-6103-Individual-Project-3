#!/usr/bin/env python
# coding: utf-8

# ## DATS 6103 - Individual Project 3 - Hao Ning 
# ## Global Scientific Research Analysis: 
# ## Scientific Articles Publication and Research Expenditure

# ### Introduction
# Science and technology are virtually the driving forces that promote the life quality of people and economic growth of a nation.  
# A detailed analysis on scienfitic research and expenditure would greatly help us to grasp the lastest trend in the world.  
# 

# ### Import packages and data

# In[1]:


# import packages
import pandas as pd
import numpy as np
get_ipython().system(' pip install pycountry')
import pycountry
import matplotlib.pyplot as plt
from IPython.display import display
import plotly
import plotly.plotly as py


# In[2]:


# plotly sign in
py.sign_in('id','api_key')
print(plotly.__version__)
plotly.offline.init_notebook_mode()


# In[3]:


# Import data set of scientific journal articles
# Research and development expenditure (% of GDP)
# GDP ($)
Sci = pd.read_csv('API_IP.JRN.ARTC.SC_DS2_en_csv_v2_10522715.csv', skiprows = 4)
ExpPercent = pd.read_csv('API_GB.XPD.RSDV.GD.ZS_DS2_en_csv_v2_10515258.csv', skiprows = 4)
GDP = pd.read_csv('API_NY.GDP.MKTP.CD_DS2_en_csv_v2_10515210.csv', skiprows = 4)
display(Sci.head())
display(ExpPercent.head())
display(GDP.head())


# ### Data cleaning

# In[4]:


# drop the region/area that are not in pycountry based on the Country Code
# get the country_code and take a look at length and first 5 code
country_code = []
for country in pycountry.countries:    
    country_code.append(country.alpha_3)

len(country_code)


# In[5]:


# set index as country code, drop region and area (that are not in country_code), leaving only countries in dataframe
Sci.new= Sci.set_index('Country Code')
# creat a droplist 
droplist = []
for x in Sci.new.index:
    if x not in country_code:
        droplist.append(x)
        
print('number of code that will be dropped:',len(droplist))
Sci.new = Sci.new.drop(droplist)
Sci.new.shape
Sci.new.tail()


# In[6]:


# rename, reset index 
Sci.new = Sci.new.rename(columns={'Country Name':'Country'}).reset_index().set_index('Country').rename(columns={'Country Code':'Code'})
Sci.new.head()


# In[7]:


# cleaning on Exp and GDP
ExpPercent.new= ExpPercent.set_index('Country Code')
ExpPercent.new = ExpPercent.new.drop(droplist)
ExpPercent.new = ExpPercent.new.rename(columns={'Country Name':'Country'}).reset_index().set_index('Country').rename(columns={'Country Code':'Code'})
display(ExpPercent.new.shape)
display(ExpPercent.new.head())

GDP.new= GDP.set_index('Country Code')
GDP.new = GDP.new.drop(droplist)
GDP.new = GDP.new.rename(columns={'Country Name':'Country'}).reset_index().set_index('Country').rename(columns={'Country Code':'Code'})
display(GDP.new.shape)
display(GDP.new.head())


# In[8]:


# find out if there's any different name in the country index
name1 = []
for x in Sci.new.index:
    if x not in ExpPercent.new.index:
        name1.append(x)
        
name2 = []
for y in ExpPercent.new.index:
    if y not in GDP.new.index:
        name2.append(y)  

name3 = []        
for z in GDP.new.index:
    if z not in Sci.new.index:
        name3.append(z)
        
print(name1, name2, name3)


# In[9]:


# rename as Macedonia, make them consistent
Sci.new.rename(index={'North Macedonia':'Macedonia'}, inplace=True)
ExpPercent.new.rename(index={'Macedonia, FYR':'Macedonia'}, inplace=True)
GDP.new.rename(index={'Macedonia, FYR':'Macedonia'}, inplace=True)


# In[10]:


# data cleaning, drop columns (Sci have no data before 2003), fillna, changed data type to int
# unit for Sci is thousand (k), so times 1000 to get the real number
Sci_clean = Sci.new.loc[:,'2003':'2016'].fillna(0).astype('int64')

Sci_clean['Code'] = Sci.new.loc[:,'Code']

Sci_clean.head()


# In[11]:


# cleaning for Exp, GDP
ExpPercent_clean = ExpPercent.new.loc[:,'2003':'2016'].fillna(0)
GDP_clean = GDP.new.loc[:,'2003':'2016'].fillna(0)

# Calculte the Expenditure in $
Exp = ExpPercent_clean*GDP_clean

# add code column, Exp is the same as GDP
ExpPercent_clean['Code'] = ExpPercent.new.loc[:,'Code']
GDP_clean['Code'] = GDP.new.loc[:,'Code']
Exp['Code'] = GDP.new.loc[:,'Code']

display(ExpPercent_clean.head())
display(GDP_clean.head())
display(Exp.head())


# In[ ]:





# ### Overview of Scientific Research Publication

# In[12]:


# For a given year, map the world Sci using plotly for year
# plotly.offline.init_notebook_mode()

def mapper(year):
    data = [dict(type='choropleth',
                 locations=Sci_clean['Code'],
                 z=Sci_clean[str(year)],
                 autocolorscale = True,
                 text=Sci_clean.index,
                 hoverinfo='text+z',
                 marker=dict(line=dict(color='rgb(180,180,180)', width=0.5)),
                 colorbar=dict(title='Number of Scientific Articles in' + str(year)))]
    
    layout = dict(title='World Number of Scientific Articles in' + str(year),
                  geo = dict(showcoastlines=False, showframe=False, projection={'type': 'equirectangular'}))

    fig = dict(data=data, layout=layout)                
    return py.iplot(fig, validate=False, filename="geomap-world_Sci")


# In[13]:


mapper(2003)


# In[14]:


mapper(2016)


# In 2003, U.S. is the only giant in scientific articles publication, followed by China, Canada, Russian, Germnay, UK and other countries.
# In 2016, U.S. and China became the two leading countries in scientific articles publication. Also, serval countries like India and Brazil showed noticably increase in publications.

# In[ ]:





# In[15]:


# plot world scientific paper publication, 2003 to 2016 (no data before 2003 )
Sci_world = Sci_clean.loc[:,'2003':'2016'].sum()

Sci_world.plot(kind='bar',figsize=(10,7), fontsize=12, color = 'firebrick')

plt.title('Number of Scientific Paper Publication by Year - World', fontsize=12)
plt.xlabel('Year', fontsize=12)
plt.ylabel('Number of Publication', fontsize=12)

plt.show()


# The total number of publication in increasing from 2003 and plateaued after 2014.

# ### Top Scientific Research Countries 

# In[16]:


# Sci top 10 countries, sort by 2016
Sci_clean.top = Sci_clean.sort_values('2016', ascending=False).drop('Code', axis=1).head(10)
Sci_clean.top


# In[17]:


# plot number of publications by year

plt.figure(figsize=(10,7))

for i in Sci_clean.top.index:
    plt.plot(Sci_clean.top.loc[i,:], marker = 'o')

plt.xlabel('Year', fontsize=12)
plt.ylabel('Number of Publications', fontsize=12)
plt.legend(bbox_to_anchor=(1, 1), fontsize=12)
plt.title('Number of Scientific Paper Publication by Year - Top 10 Countries', fontsize=12)

plt.show()


# For USA, the number of publication showed a little increase then followed by a drop after 2014.  
# China showed dramatic increase in publication numbers. India and Brazil also showed steady increase.  
# Now, let's take a look at the details for individual year.

# In[18]:


# for a given year and dataframe, get the top 10 countries 

def topten(year,data,total=10):
    df = data[str(year)]
    top = df.sort_values(ascending=False)
    top = top.reset_index().head(total)
    top.index = top.index + 1
    return top


# In[19]:


# for a given year and dataframe, make a pie chart of the top 10 and the rest countries

def PiePlot(year, data):
    df = data[str(year)]
    top = df.sort_values(ascending=False)
    top = top.reset_index()
    top.index = top.index + 1
    others = top[10:].sum()[1]
    top = top[:10]
    top.loc[11] = ['All Other Countries', others]
    
    countryPlot = top[str(year)].plot.pie(subplots=True,
                                     autopct='%0.2f',
                                     fontsize=12,
                                     figsize=(10,10),
                                     legend=False,
                                     labels=top['Country'],
                                     shadow=False,
                                     explode=(0.15,0,0,0,0,0,0,0,0,0,0),
                                     startangle=90)
    plt.show()


# In[20]:


topten(2003,Sci_clean)


# In[21]:


PiePlot(2003,Sci_clean)


# In[22]:


topten(2016,Sci_clean)


# In[23]:


PiePlot(2016,Sci_clean)


# From 2003 to 2016:    
# USA have a dominating number of publications in 2003.   
# China climbed from 3rd place to top rank, the number of publication is similar to USA in 2016.   
# Japan's rank is 2nd then falling to 6th.   
# Korea, Rep. is new to top10.   
# Other than the top 10 countries, the rest countries also showed a higher share of total publication. It's a indication that all coutries are putting more efforts in scientific research.

# ### Change of Number of Publication of Top Countries in Absolute and Percentage

# In[24]:


# absolute change
Sci_change = Sci_clean.top.diff(axis=1).fillna(value=0)

Sci_change


# In[25]:


# percentage change
Sci_pchange = (Sci_clean.top.pct_change(axis=1) * 100).fillna(value=0)

Sci_pchange


# In[26]:


# make the absolute and percentage change plot

Sci_change.plot(kind='bar', colormap='plasma', figsize=(12,8), rot=45, fontsize=10)
plt.xlabel('Country', fontsize=10)
plt.ylabel('Absolute Change', fontsize=10)
plt.legend(bbox_to_anchor=(1, 1), fontsize=10)
plt.axhline(0, linestyle='dashed',linewidth=1, color='grey')
plt.title('Publication Growth - Absolute', fontsize=10)


Sci_pchange.plot(kind='bar',colormap= 'viridis', figsize=(12,8), rot=45, fontsize=10)
plt.xlabel('Country', fontsize=10)
plt.ylabel('Percentage Change (%)', fontsize=10)
plt.legend(bbox_to_anchor=(1, 1), fontsize=10)
plt.axhline(0, linestyle='dashed',linewidth=1, color='grey')
plt.title('Publication Growth - Percentage (%)', fontsize=10)

plt.show()


# China and USA showed greatest growth in absolute number overall. However, there's a drop obersered for recent years for USA.  
# Also, India and Korea, Rep. have steady increase.  
# 
# China showed fastest growing in percentage. Followed by India, Korea, Rep.and Russia.

# ### Research Expenditure Analysis

# In[27]:


# global total expenditure comparing with publication
# bar-line plot, bar expenditure, line publication
fig, ax1 = plt.subplots(figsize=(12,8))
   
df1 = Exp.drop('Code', axis=1).sum()
df2 = Sci_world

ax1=df1.plot(kind='bar',width = 0.5, color = 'g')
ax2 = ax1.twinx()
ax2=df2.plot(color='r')

ax1.set_ylabel('Research Expenditure ($)- Green Bar', fontsize=12)
ax2.set_ylabel('Number of Publication - Red Line', fontsize=12)
   
plt.show()


# The total expenditure keep increasing (with small fluctuations) from 2003 and reached stagnant after 2013.
# 
# The overall trend of publication and research expenditure coincides.  

# In[28]:


# get top country index with top publication, find the data in Exp($)
Exp.top = Exp.loc[Sci_clean.top.index].drop('Code', axis=1)
Exp.top


# In[29]:


# There're a few 0 in the dataframe (India), let's fill it with the value of previous column
Exp.fill= Exp.replace(0, np.nan).ffill(axis=1)
Exp.top.fill = Exp.top.replace(0, np.nan).ffill(axis=1)
Exp.top.fill


# In[30]:


# plot the expenditure for top countries by year

plt.figure(figsize=(10,7))

for i in Exp.top.fill.index:
    plt.plot(Exp.top.fill.loc[i,:], marker = 'o')

plt.xlabel('Year', fontsize=12)
plt.xticks(rotation=45, fontsize=12)
plt.ylabel('Expenditure ($)', fontsize=12)
plt.legend(bbox_to_anchor=(1, 1), fontsize=12)
plt.title('Research Expenditure ($) by Year - Top 10 Countries', fontsize=12)

plt.show()


# In[31]:


# Expenditure (% of GDP) of top countries,ffill India
ExpPercent.top = ExpPercent_clean.loc[Sci_clean.top.index].drop('Code', axis=1)
ExpPercent.top.fill = ExpPercent.top.replace(0, np.nan).ffill(axis=1)
ExpPercent.top.fill


# In[32]:


# plot the expenditure (% of GDP) for top countries by year

plt.figure(figsize=(10,7))

for i in ExpPercent.top.fill.index:
    plt.plot(ExpPercent.top.fill.loc[i,:], marker = 'o')

plt.xlabel('Year', fontsize=12)
plt.xticks(rotation=45, fontsize=12)
plt.ylabel('Expenditure (% of GDP)', fontsize=12)
plt.legend(bbox_to_anchor=(1, 1), fontsize=12)
plt.title('Research Expenditure (% of GDP) by Year - Top 10 Countries', fontsize=12)

plt.show()


# In[33]:


topten(2003,Exp)


# In[34]:


PiePlot(2003,Exp)


# In[35]:


topten(2016,Exp)


# In[36]:


PiePlot(2016,Exp)


# Both USA and China raised their research expenditure in terms of the absolute amount.   
# Interestingly, the growth rate (slope) of this two countries coincides with each other.    
# Korea showed steady increase.  
# The rest countries don't have extraordinary change in expenditure. 
# USA have an dominating research expenditure percentage.
# 
# Note: India has few missing value because of the data set, the value is filled by previous column.

# **Japan** is maintaining a very high expenditure % of GDP among all the countries, up to 3%.    
# Followed by USA and Gemany around 2.5-2.8%.  
# **Korea** significantly raised the expenditure % to more than 4%.  
# China also increased the percentage from 1 to 2 %.   

#  
# ### Correlation between Publication and Research Expenditure

# In[37]:


# scatter plot of Expenditure vs publications
# scatterf plot of log number

fig, ax = plt.subplots(1,2,figsize=(12,6))

x1=Exp.drop('Code', axis=1)
y1=Sci_clean.drop('Code', axis=1)

x2=np.log(Exp.drop('Code', axis=1))
y2=np.log(Sci_clean.drop('Code', axis=1))

plt.subplot(1,2,1)
plt.scatter(x1,y1, s=7)
plt.title('Publication - Expenditure')

plt.subplot(1,2,2)
plt.scatter(x2,y2, s=5)
plt.title('Publication - Expenditure - log')

plt.tight_layout()
plt.show()


# Obviously, a positive correlation is observed that a higher research expenditure would lead to more publications.  
# 
# For the actually number plot, we can see the data points are splitting apart, it will be interesting to further explore the 'productivity'.  
# 
# For the log plot, a pretty clear linear relation is observed.  
# Also, for higher expenditure, the data points are more concentrated, while for lower expenditure, data points are more scattered.  

# Overall, countries with higher expenditure will have more publications.  
# 
# #### Most Productive Countries

# In[38]:


# calcultate publication/expenditure ratio, higher ratio indicates the country is more productive
# India have missing value, serveal year will be inf after calculation, replace using ffill
ratio = Sci_clean.top/Exp.top
ratio.fill = ratio.replace(np.inf, np.nan).ffill(axis=1)
ratio.fill


# In[39]:


# plot the ratio
plt.figure(figsize=(12,8))

for i in ratio.fill.index:
    plt.plot(ratio.fill.loc[i,:], marker = 'o')

plt.xlabel('Year', fontsize=12)
plt.xticks(rotation=45, fontsize=12)
plt.ylabel('Ratio', fontsize=12)
plt.legend(bbox_to_anchor=(1, 1), fontsize=12)
plt.title('Publication/Expenditure Ratio - Top 10 Countries', fontsize=12)

plt.show()


# India showed highest productivity overall.  
# China have a very high productivity ratio at 2003 to 2005 then decreased and stablized, still among top 5.  
# Russia showed a "U" shape curve.  
# The rest countries showed similar ratio. 
# 
# We can see that, the developing countries showed a great rise in publication output. Productivity is one aspect of scientific research, on the other hand, developed countries probably are more dominating in citations.
# 
# 
# Note: India has few missing value because of the data set, the value is filled by previous column. 

# ### Summary
# 
# * From 2003 to 2016, the number of global publication keep increasing then plateaued after 2014.  
# * USA was the only giant in publication in 2003, while in 2016, China climbed up to top and these two countries became the flagships.  
# * USA has an dominating expenditure in scientific research
# * Japan, USA and Germany are maintaining a high research expenditure % of GDP (2.5-3%).
# * Korea dramatically increased their expenditure % ( >4% in 2016) and became top10.
# * Positive correlation is observed for publication/expenditure, but indicating differences in 'productivity'
# * India, Russia and China are the most 'productive' countries
#  

# ### References
# 
# 
# * Jeff Tollefson. "China declared world’s largest producer of scientific articles", Nature, Volume 553, Issue 7689, pp. 390 (2018). DOI: 10.1038/d41586-018-00927-4
# * Lee-Roy Chetty. 2012. "The Role of Science and Technology in the Developing World in the 21st Century", URL: https://ieet.org/index.php/IEET2/more/chetty20121003
# * Karen E. White, Carol Robbins, Beethika Khan, and Christina Freyman. 2017. "Science and Engineering Publication Output Trends: 2014 Shows Rise of Developing Country Output while Developed Countries Dominate Highly Cited Publications", URL: https://www.nsf.gov/statistics/2018/nsf18300/
# 
# 

# ### Project 3 Complete, thank you!

# In[ ]:





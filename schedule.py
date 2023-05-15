from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import main

import numpy as np
df = pd.read_csv('./cost_production.sdv', sep=";", decimal=',') # thousands = ',' fixes object/string conversions
df = df.fillna(0)
df.loc[df['Sum'] < 0, 'Sum'] = 0 # replace values below 0 for all columns with ['Sum'].

datacenters = pd.read_csv('./datacenters.csv', sep=';', decimal=',')
#nord = pd.read_csv('fullset_nordics.sdv', sep=";", decimal=',')
nord = pd.read_csv('nordic_baltics.csv', sep=";", decimal=',')
nord = nord.fillna(0)
nord.loc[nord['Sum'] < 0, 'Sum'] = 0

# Currency conversions
# 21.3.2013
# EUR:NOK -> 11.549
# EUR:SEK -> 11.173
# EUR:DKK -> 7.447


alias_no = ['NO1', 'NO2', 'NO3', 'NO4', 'NO5']
nok_euro = (nord['Datatype'] == 'PR') & (nord['Kode'] == 'XO') & (nord['Alias'].isin(alias_no))
nord.loc[nok_euro, 'Sum'] /=11.549
alias_se = ['SE1', 'SE2', 'SE3', 'SE4']
sek_euro = (nord['Datatype'] == 'PR') & (nord['Kode'] == 'XO') & (nord['Alias'].isin(alias_se))
nord.loc[sek_euro, 'Sum'] /=11.173
alias_dk = ['DK1', 'DK2']
dkk_euro = (nord['Datatype'] == 'PR') & (nord['Kode'] == 'XO') & (nord['Alias'].isin(alias_dk))
nord.loc[dkk_euro, 'Sum'] /= 7.447



def finnradindex(frame, value):
    temp = frame["Sum"] == value 
    # Search for value in production frame
    new_df = pd.DataFrame(temp) 
    # go from series to Dataframe.
    result = new_df.query("Sum") 
    # returns only the value which is true.
    return result.Sum.index.values.max() 
  # return the float value of the index to search for with df.iloc[x]




def writeFile(inputframe, index):
    """

    :param inputframe: Should be the original dataframe not processed.
    :param index: Index returned from finnradindex
    :return: none, writes file to disk.
    """
    with open(f'{datetime.now().strftime("%Y-%m-%d_%H-%M")} {str(inputframe.iloc[index].Alias)}', 'w') as f:
        f.write(
            f'Deployed at: {datetime.now().strftime("%Y-%m-%d_%H-%M")}\n'
            f'Data for deployment:\n\n'
            f'{inputframe.iloc[index]}'
        )

def daysum(frame):
    return frame.Sum

def calcminmax(frame):
    temp = daysum(frame)
    temp = temp
    resmin = temp.values.min()
    resmax = temp.values.max()
    return [resmin, resmax]


def bestfit(frame, dato, cost=False):
    """
    Find the best fit in current data, best fit is determined as the most green.
    @:param: frame, accepts a dataframe
    @:param: dato, date in the dd-mm-yyyy %d-%m-%Y format.
    @:param: cost is none by default, this finds bestfit for production. Set to True to go get cost.
    :return:
    """
    if cost is False:
        datatype_value = 'PS'
        kode_value = 'P'
    else:
        datatype_value = 'PR'
        kode_value = 'XO'

    # Copy frame
    tmp = frame.copy()

    # Prepare date
    dato = dato

    # Convert df['Dato'] to proper dateformat.
    tmp['Dato'] = pd.to_datetime(tmp['Dato'], format='%d.%m.%Y')

    # Pull correct data types from frame.
    tmp = tmp[(tmp['Datatype'] == datatype_value) & (tmp['Kode'] == kode_value) & (tmp['Dato'] == dato)]

    # Create new dataframe to return using the main dataframe columns.
    result = pd.DataFrame(columns=tmp.columns)
    if cost == True:
        addthis = nord.iloc[finnradindex(tmp, calcminmax(tmp)[0])]
        result = result.append(addthis, ignore_index=True)
        return result
    else:
        addthis = nord.iloc[finnradindex(tmp, calcminmax(tmp)[1])]
        result = result.append(addthis, ignore_index=True)
        return result


def bestfit_wind(frame, dato):
    """
    Find the best fit in current data, best fit is determined as the most green.
    @:param: frame, accepts a dataframe
    @:param: dato, date in the dd-mm-yyyy %d-%m-%Y format.
    @:param: cost is none by default, this finds bestfit for production. Set to True to go get cost.
    :return:
    """

    datatype_value = 'PS'
    kode_value = 'WS'
    # Copy frame
    tmp = frame.copy()

    # Prepare date
    dato = dato

    # Convert df['Dato'] to proper dateformat.
    tmp['Dato'] = pd.to_datetime(tmp['Dato'], format='%d.%m.%Y')

    # Pull correct data types from frame.
    tmp = tmp[(tmp['Datatype'] == datatype_value) & (tmp['Kode'] == kode_value) & (tmp['Dato'] == dato)]

    # Get the min/max values for cost/prod
    getmin = calcminmax(tmp)[0]
    getmax = calcminmax(tmp)[1]

    # Get the corresponding row index to get it from the clean dataframe.
    lowcostrow = finnradindex(tmp, getmin)
    higprodrow = finnradindex(tmp, getmax)

    # Create new dataframe to return using the main dataframe columns.
    result = pd.DataFrame(columns=tmp.columns)

    addthis = nord.iloc[finnradindex(tmp, calcminmax(tmp)[1])]
    result = result.append(addthis, ignore_index=True)
    return result


def filter_dataframe(nord, cost = None):
    if cost is None:
        datatype_value = 'PS'
        kode_value = 'P'
    else:
        datatype_value = 'PR'
        kode_value = 'XO'
    # Make a copy of the input DataFrame
    filtered_df = nord.copy()

    # Filter by datatype, Kode and Alias
    #filtered_df = filtered_df[(filtered_df['Datatype'] == datatype_value) & (filtered_df['Kode'] == kode_value) & ((filtered_df['Alias'] == "NO1") | (filtered_df['Alias'] == "SE3") | (filtered_df['Alias'] == "FI") | (filtered_df['Alias'] == "DK1"))]

    # Filtered for all countries and regions in the nordic and baltic regions.
    # filtered_df = filtered_df[(filtered_df['Datatype'] == datatype_value) & (filtered_df['Kode'] == kode_value) & ((filtered_df['Alias'] == "NO1") | (filtered_df['Alias'] == "NO2") | (filtered_df['Alias'] == "NO3") | (filtered_df['Alias'] == "NO4") | (filtered_df['Alias'] == "NO5") | (filtered_df['Alias'] == "SE1") | (filtered_df['Alias'] == "SE2") | (filtered_df['Alias'] == "SE3") | (filtered_df['Alias'] == "LV") | (filtered_df['Alias'] == "LT") | (filtered_df['Alias'] == "EE") | (filtered_df['Alias'] == "FI") | (filtered_df['Alias'] == "DK1"))]
    
    # Filtered for wind, only for plotting
    filtered_df = filtered_df[(filtered_df['Datatype'] == 'PS') & (filtered_df['Kode'] == 'WS') & ((filtered_df['Alias'] == "NO1") | (filtered_df['Alias'] == "NO2") | (filtered_df['Alias'] == "NO3") | (filtered_df['Alias'] == "NO4") | (filtered_df['Alias'] == "NO5") | (filtered_df['Alias'] == "SE1") | (filtered_df['Alias'] == "SE2") | (filtered_df['Alias'] == "SE3") | (filtered_df['Alias'] == "LV") | (filtered_df['Alias'] == "LT") | (filtered_df['Alias'] == "EE") | (filtered_df['Alias'] == "FI") | (filtered_df['Alias'] == "DK1"))]


    # for control only
    #filtered_df = filtered_df[(filtered_df['Datatype'] == datatype_value) & (filtered_df['Kode'] == kode_value) & ((filtered_df['Alias'] == "NO1"))]

    # Format the Dato column to a datetime object
    filtered_df['Dato'] = pd.to_datetime(filtered_df['Dato'], format='%d.%m.%Y')

    # Select the desired columns
    filtered_df = filtered_df[['Datatype', 'Kode', 'Alias', 'Dato', 'Sum']]

    # Filter by the month of March
    start_date = pd.to_datetime('2023-03-01')
    end_date = pd.to_datetime('2023-03-31')
    filtered_df = filtered_df[(filtered_df['Dato'] >= start_date) & (filtered_df['Dato'] <= end_date)]

    return filtered_df
  

def result_stack():
    # Get the output DataFrame from function_a
    result = nord.loc[nord.index == bestfit(month)] # intricate, bestfit(df) gets the index of the row with the best fit value and checks if true, if true returns the dataframe.

    # Create a new empty DataFrame with the same format as the output of function_a
    df_format = pd.DataFrame(columns=result.columns)

    # Append the format DataFrame to the result DataFrame to create a new clean DataFrame
    df = df_format.append(result, ignore_index=True)

    return df

  
month = filter_dataframe(nord)
monthcost = filter_dataframe(nord, cost=True)

experiment = pd.DataFrame(columns=month.columns)
experiment['Dato'] = pd.to_datetime(experiment['Dato'], format='%d.%m.%Y')

experiment_cost = pd.DataFrame(columns=monthcost.columns)
experiment_cost['Dato'] = pd.to_datetime(experiment_cost['Dato'], format='%d.%m.%Y')

datoer = datelist('2023-03-01', 31)

for element in datoer:
    experiment = experiment.append(bestfit(month, element, cost=False), ignore_index=True)
experiment['Dato'] = pd.to_datetime(experiment['Dato'], format='%d.%m.%Y')


for k in datoer:
    experiment_cost = experiment_cost.append(bestfit(monthcost, k, cost=True), ignore_index=True)
experiment_cost['Dato'] = pd.to_datetime(experiment_cost['Dato'], format='%d.%m.%Y')


def deployVM(dfa, date, cost=False):
    """
    Special function only for demonstration purposes at this time.
    Use month or monthcost, not experiment frames, experiment will return strange data due to wrong indexes.
    """
    alias = bestfit_b(dfa, date, cost=cost)
    result = alias['Alias'].to_string(index=False)

    if result == 'NO1':
        main.writeAzure()
    elif result == 'FI':
        main.writeGoogle()
    elif result == 'SE3':
        main.writeAws()

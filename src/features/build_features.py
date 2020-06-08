import numpy as np
from sklearn import linear_model
from scipy import signal
import pandas as pd

reg=linear_model.LinearRegression(fit_intercept=True)

def doubling_time_linear_regression(in_array):
    '''Approximate doubling rate using linear regression'''
    #y=np.array(in_array)
    #X=np.arange(-1,2).reshape(-1,1)

    y=np.array(in_array)
    X=np.arange(len(y)).reshape(-1,1)

    assert len(in_array)==3
    reg.fit(X,y)

    doubling_rate = reg.intercept_/reg.coef_ #intercept/slope
    return doubling_rate

def savgol_filter(df_input, column='confirmed', window=5):
    '''
    Apply savgol filter to rows
    '''
    degree=1
    df_result=df_input
    filter_in=df_input[column].fillna(0)
    result=signal.savgol_filter(np.array(filter_in),window, degree)

    df_result[column+'_filtered']=result
    return df_result

def rolling_reg(df_input, col='confirmed'):
    days_back=3
    result=df_input[col].rolling(
        window=days_back,
        min_periods=days_back
    ).apply(doubling_time_linear_regression, raw=False)

    return result

def calc_filtered_data(df_input, filter_on='confirmed'):
    '''
    Calculate filter value and return merged dataframe
    '''
    must_contain=set(['state', 'country', filter_on])
    assert must_contain.issubset(set(df_input.columns)) , 'Error in calc_filtered_data not all columns in dataframe'

    pd_filtered_result = df_input[['state', 'country', filter_on]].groupby(['state', 'country']).apply(savgol_filter).reset_index()
    df_output = pd.merge(df_input, pd_filtered_result[['index', filter_on+'_filtered']], on=['index'], how='left')

    return df_output

def calc_doubling_rate(df_input, filter_on='confirmed'):
    '''
    Calculate approximated doubling rate and return merged dataframe
    '''
    must_contain=set(['state', 'country', filter_on])
    assert must_contain.issubset(set(df_input.columns)) , 'Error in calc_doubling_rate not all columns in dataframe'

    pd_dr_result = df_input.groupby(['state', 'country']).apply(rolling_reg, filter_on).reset_index()
    pd_dr_result = pd_dr_result.rename(columns={
        filter_on:filter_on+'_dr',
        'level_2':'index'
        })

    df_output = pd.merge(df_input, pd_dr_result[['index', filter_on+'_dr']], on=['index'], how='left')

    return df_output



if __name__ == '__main__':
    test_data=np.array([2,4,6])
    result=doubling_time_linear_regression(test_data)
    print('The test slope is: '+ str(result))

    pd_data=pd.read_csv('data/processed/COVID_relational_confirmed.csv', sep=";",parse_dates=[0])
    pd_data=pd_data.sort_values('date', ascending=True).reset_index().copy()

    pd_result=calc_filtered_data(pd_data)
    pd_result=calc_doubling_rate(pd_result)
    pd_result=calc_doubling_rate(pd_result,'confirmed_filtered')
    print(pd_result.head())

    mask=pd_result['confirmed']>100
    pd_result['confirmed_filtered_dr']=pd_result['confirmed_filtered_dr'].where(mask, other=np.NaN)
    pd_result.to_csv('data/processed/COVID_final_set.csv',sep=';',index=False)
    print(pd_result[pd_result['country']=='US'].tail())
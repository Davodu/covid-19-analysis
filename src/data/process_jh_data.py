import pandas as pd
import numpy as np

from datetime import datetime

def store_relational_jh_data():
    data_path='../data/raw/COVID-19/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
    pd_raw=pd.read_csv(data_path)

    pd_data_base=pd_raw.rename(columns={'Province/State':'state', 'Country/Region':'country'})
    pd_data_base['state'] = pd_data_base['state'].fillna('no')
    pd_data_base=pd_data_base.drop(['Lat','Long'], axis=1)

    df_relational=pd_data_base.set_index(['state', 'country'])\
                    .T\
                    .stack(level=[0,1])\
                    .reset_index()\
                    .rename(columns={
                        'level_0':'date',
                        0:'confirmed'
                    })
    #set date to datetime
    df_relational['date']=df_relational.date.astype('datetime64[ns]')
    df_relational.to_csv('../data/processed/COVID_relational_confirmed.csv', sep=';', index=False)
    print('Number of rows stored: ' + str(df_relational.shape[0]))

if __name__ == '__main__':
    store_relational_jh_data()
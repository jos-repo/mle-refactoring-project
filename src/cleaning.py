import pandas as pd
import numpy as np
from datetime import datetime
 

def open_king_country_hous_prices_data():
    open_house_prices = pd.read_csv("./data/King_County_House_prices_dataset.csv")
    open_house_prices_data = open_house_prices.copy()
    return open_house_prices_data

def remove_outlier_with_high_bedroom_bathroom_ratio():
    remove_outlier = open_king_country_hous_prices_data()[(\
        open_king_country_hous_prices_data()['bedrooms'] /\
            open_king_country_hous_prices_data()['bathrooms']) <= 10]
    return remove_outlier

def inputation_sqft_basement():
    sqft_basement = remove_outlier_with_high_bedroom_bathroom_ratio()
    sqft_basement['sqft_basement'] = sqft_basement['sqft_basement'].replace('?', np.NaN)
    sqft_basement['sqft_basement'] = sqft_basement['sqft_basement'].astype(float)
    sqft_basement.eval('sqft_basement = sqft_living - sqft_above', inplace=True)
    return sqft_basement

def inputation_view_values():
    view_values = inputation_sqft_basement()
    view_values['view'].fillna(0, inplace=True)
    return view_values

def inputation_waterfront_values():
    waterfront_values = inputation_view_values()
    waterfront_values.waterfront.fillna(0, inplace=True)
    return waterfront_values

def last_change_on_building():
    renovation = inputation_waterfront_values()
    last_known_change = []
    for idx, yr_re in renovation.yr_renovated.items():
        if str(yr_re) == 'nan' or yr_re == 0.0:
            last_known_change.append(renovation.yr_built[idx])
        else:
            last_known_change.append(int(yr_re))
    renovation['last_known_change'] = last_known_change
    renovation.drop("yr_renovated", axis=1, inplace=True)
    renovation.drop("yr_built", axis=1, inplace=True)
    return renovation

def date_format():
    date_format = last_change_on_building()
    date_format['date'] = pd.to_datetime(date_format['date'])
    return date_format
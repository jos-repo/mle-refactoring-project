import pandas as pd
import numpy as np
from datetime import datetime
from pydantic import BaseModel
from cleaning import clean_df

class DataValidation(BaseModel):
    id: int
    date: datetime
    price: float 
    bedrooms: int 
    bathrooms: float  
    sqft_living: int 
    sqft_lot: int 
    floors: float
    waterfront: float
    view: float 
    condition: int 
    grade: int  
    sqft_above: int 
    sqft_basement: float 
    last_known_change: int
    zipcode: int 
    lat: float 
    long: float  
    sqft_living15: int 
    sqft_lot15: int 
    sqft_price: float
    delta_lat: float
    delta_long: float
    center_distance: float
    water_distance: float

def data_validation(df: pd.DataFrame, data_schema) -> pd.DataFrame:
    class DataframeValidation(BaseModel):
        df_as_dict: list[data_schema]
    df_as_dict = df.to_dict(orient='records')
    DataframeValidation(df_as_dict=df_as_dict)
    return df 

def distance_to_water(long, lat, ref_long, ref_lat):
    delta_long = long - ref_long
    delta_lat = lat - ref_lat
    delta_long_corr = delta_long * np.cos(np.radians(ref_lat))
    return ((delta_long_corr)**2 +(delta_lat)**2)**(1/2)*2*np.pi*6378/360

def feature_engineering():
    house_prices_feature_engineering = clean_df()

    house_prices_feature_engineering['sqft_price'] = (house_prices_feature_engineering.price/(\
        house_prices_feature_engineering.sqft_living + house_prices_feature_engineering.sqft_lot)).round(2)

    house_prices_feature_engineering['delta_lat'] = np.absolute(47.62774- house_prices_feature_engineering['lat'])
    house_prices_feature_engineering['delta_long'] = np.absolute(-122.24194-house_prices_feature_engineering['long'])
    house_prices_feature_engineering['center_distance']= ((house_prices_feature_engineering['delta_long']* np.cos(np.radians(47.6219)))**2 
                                    + house_prices_feature_engineering['delta_lat']**2)**(1/2)*2*np.pi*6378/360

    water_list= house_prices_feature_engineering.query('waterfront == 1')
    water_distance = []
    for idx, lat in house_prices_feature_engineering.lat.items():
        ref_list = []
        for x,y in zip(list(water_list.long), list(water_list.lat)):
            ref_list.append(distance_to_water(house_prices_feature_engineering.long[idx], house_prices_feature_engineering.lat[idx],x,y).min())
        water_distance.append(min(ref_list))
    house_prices_feature_engineering['water_distance'] = water_distance
    
    data_validation(house_prices_feature_engineering, DataValidation)
    return house_prices_feature_engineering

q2 = feature_engineering()

print(q2)
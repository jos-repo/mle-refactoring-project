import pandas as pd
import numpy as np
from datetime import datetime
from pydantic import BaseModel
from cleaning import date_format

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

def distance_calculater(long, lat, ref_long, ref_lat):
    delta_long = long - ref_long
    delta_lat = lat - ref_lat
    delta_long_corr = delta_long * np.cos(np.radians(ref_lat))
    return ((delta_long_corr)**2 +(delta_lat)**2)**(1/2)*2*np.pi*6378/360

def calculate_sqft_price():
    price_per_sqft = date_format()
    price_per_sqft['sqft_price'] = (price_per_sqft.price/(price_per_sqft.sqft_living + price_per_sqft.sqft_lot)).round(2)
    return price_per_sqft

def calculata_center_distance():
    distance = calculate_sqft_price()
    distance['delta_lat'] = np.absolute(47.62774- distance['lat'])
    distance['delta_long'] = np.absolute(-122.24194-distance['long'])
    distance['center_distance']= ((distance['delta_long']* np.cos(np.radians(47.6219)))**2 
                                    + distance['delta_lat']**2)**(1/2)*2*np.pi*6378/360
    return distance

def calculate_waterfront_distance():
    distance = calculata_center_distance()
    water_list= distance.query('waterfront == 1')
    water_distance = []
    for idx, lat in distance.lat.items():
        ref_list = []
        for x,y in zip(list(water_list.long), list(water_list.lat)):
            ref_list.append(distance_calculater(distance.long[idx], distance.lat[idx],x,y).min())
        water_distance.append(min(ref_list))
    distance['water_distance'] = water_distance
    return distance

def validation_df():
    validation_df = calculate_waterfront_distance()
    df = data_validation(validation_df, DataValidation)
    return df

df = validation_df()

print(df)
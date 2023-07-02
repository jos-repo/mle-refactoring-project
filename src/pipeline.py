import pandas as pd
import numpy as np
from datetime import datetime
from pydantic import BaseModel
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline

def house_prices_data():
    open_house_prices = pd.read_csv("./data/King_County_House_prices_dataset.csv")
    open_house_prices_data = open_house_prices.copy()
    return open_house_prices_data

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
    zipcode: int
    lat: float 
    long: float  
    sqft_living15: int 
    sqft_lot15: int 
    last_known_change: int
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


#  Data cleaning
class removeOutlier(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self
    
    def transform(self, X, y=None):
        X = X[(X['bedrooms'] / X['bathrooms']) <= 10]                                
        return X

class sqftBasementTransformer(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self
    
    def transform(self, X, y=None):
        X = X.copy()
        X['sqft_basement'] = X['sqft_basement'].replace('?', np.NaN)
        X['sqft_basement'] = X['sqft_basement'].astype(float)
        X.eval('sqft_basement = sqft_living - sqft_above', inplace=True)                               
        return X

class viewTransformer(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self
    
    def transform(self, X, y=None):
        X['view'].fillna(0, inplace=True)                             
        return X

class waterfrontTransformer(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self
    
    def transform(self, X, y=None):
        X.waterfront.fillna(0, inplace=True)                             
        return X

class lastChangeTransformer(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self
    
    def transform(self, X, y=None):
        last_known_change = []
        for idx, yr_re in X.yr_renovated.items():
            if str(yr_re) == 'nan' or yr_re == 0.0:
                last_known_change.append(X.yr_built[idx])
            else:
                last_known_change.append(int(yr_re))
        X['last_known_change'] = last_known_change
        X.drop('yr_renovated', axis=1, inplace=True)
        X.drop("yr_built", axis=1, inplace=True)
        return X

class dateTransformer(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self
    
    def transform(self, X, y=None):
        X['date'] = pd.to_datetime(X['date'])#, format='%Y/%m/%d').astype('object')                       
        return X


# Data engineering
def distance_calculater(long, lat, ref_long, ref_lat):
    delta_long = long - ref_long
    delta_lat = lat - ref_lat
    delta_long_corr = delta_long * np.cos(np.radians(ref_lat))
    return ((delta_long_corr)**2 +(delta_lat)**2)**(1/2)*2*np.pi*6378/360

class sqftPriceCalculator(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self
    
    def transform(self, X, y=None):
        X['sqft_price'] = (X.price/(X.sqft_living + X.sqft_lot)).round(2)                       
        return X
    
class centerDistanceCalculator(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self
    
    def transform(self, X, y=None):
        X['delta_lat'] = np.absolute(47.62774- X['lat'])
        X['delta_long'] = np.absolute(-122.24194-X['long'])
        X['center_distance']= ((X['delta_long']* np.cos(np.radians(47.6219)))**2 
                                    + X['delta_lat']**2)**(1/2)*2*np.pi*6378/360                       
        return X

class waterfrontCalculator(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self
    
    def transform(self, X, y=None):
        water_list= X.query('waterfront == 1')
        water_distance = []
        for idx, lat in X.lat.items():
            ref_list = []
            for x,y in zip(list(water_list.long), list(water_list.lat)):
                ref_list.append(distance_calculater(X.long[idx], X.lat[idx],x,y).min())
            water_distance.append(min(ref_list))
        X['water_distance'] = water_distance
        return X


# Pipeline for cleaning and engineering
def pipelines_for_cleaning_engineering():
    data_cleaning_pipeline = Pipeline([
        ('remove_outlier', removeOutlier()),
        ('sqft_basement_transformer', sqftBasementTransformer()),
        ('view_transformer', viewTransformer()),
        ('waterfront_transformer', waterfrontTransformer()),
        ('last_change_transformer', lastChangeTransformer()),
        ('date_transformer', dateTransformer())
        ])

    data_engineering_pipeline = Pipeline([
        ('sqft_Price_Calculator', sqftPriceCalculator()),
        ('center_Distance_Calculator', centerDistanceCalculator()),
        ('waterfront_Calculator', waterfrontCalculator())
        ])

    preprocessor_pipe = Pipeline([
        ('data_cleaning', data_cleaning_pipeline),
        ('data_engineering', data_engineering_pipeline)
        ])
    return preprocessor_pipe


def clean_data():
    house_prices_sklearn = house_prices_data()
    preprocessor_pipe = pipelines_for_cleaning_engineering()
    clean_data = preprocessor_pipe.fit_transform(house_prices_sklearn)
    return clean_data

def validated_data():
    validation = clean_data()
    validated_data = data_validation(validation, DataValidation)
    return validated_data


df = validated_data()
df.info()
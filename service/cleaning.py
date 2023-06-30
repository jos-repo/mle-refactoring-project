import pandas as pd
import numpy as np
from datetime import datetime
 

def clean_df():
    king_country_house_prices = pd.read_csv("./data/King_County_House_prices_dataset.csv")
    king_country_house_prices_cleaning = king_country_house_prices.copy()

    king_country_house_prices_cleaning = king_country_house_prices_cleaning[(\
        king_country_house_prices_cleaning['bedrooms'] /\
            king_country_house_prices_cleaning['bathrooms']) <= 10]

    king_country_house_prices_cleaning['sqft_basement'] = king_country_house_prices_cleaning['sqft_basement'].replace('?', np.NaN)
    king_country_house_prices_cleaning['sqft_basement'] = king_country_house_prices_cleaning['sqft_basement'].astype(float)
    king_country_house_prices_cleaning.eval('sqft_basement = sqft_living - sqft_above', inplace=True)
    king_country_house_prices_cleaning['view'].fillna(0, inplace=True)
    king_country_house_prices_cleaning.waterfront.fillna(0, inplace=True)

    last_known_change = []
    for idx, yr_re in king_country_house_prices_cleaning.yr_renovated.items():
        if str(yr_re) == 'nan' or yr_re == 0.0:
            last_known_change.append(king_country_house_prices_cleaning.yr_built[idx])
        else:
            last_known_change.append(int(yr_re))
    king_country_house_prices_cleaning['last_known_change'] = last_known_change
    king_country_house_prices_cleaning.drop("yr_renovated", axis=1, inplace=True)
    king_country_house_prices_cleaning.drop("yr_built", axis=1, inplace=True)

    king_country_house_prices_cleaning['date'] = pd.to_datetime(king_country_house_prices_cleaning['date'])

    return king_country_house_prices_cleaning
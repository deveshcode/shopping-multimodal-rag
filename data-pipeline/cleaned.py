import pandas as pd
df=pd.read_csv('nike_mens_clothing_with_additional_data.csv')
# Remove everything after "Shown:"
df['Description'] = df['Description'].str.split('Shown: ').str[0]
df.to_csv('nike_mens_clothing_with_additional_data_cleaned.csv')
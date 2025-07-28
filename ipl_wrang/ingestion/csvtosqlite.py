import pandas as pd
import sqlite3
from utils import common

df = pd.read_csv('cleaned_data/deliveries_cleaned.csv')
conn = sqlite3.connect('ipl_data.db') 
df.to_sql('matches', conn, if_exists='replace', index=False)
conn.close()
print("CSV data saved to SQLite successfully!")

df = pd.read_csv('cleaned_data/matches_cleaned.csv')
conn = sqlite3.connect('ipl_data.db')
df.to_sql('matches', conn, if_exists='replace', index=False)
conn.close()
print("CSV data saved to SQLite successfully!")
import pandas as pd
import sqlite3
import re
import os

def extract_data():
    """Extract all raw data."""
    matches = pd.read_csv('../data/matches.csv')
    deliveries = pd.read_csv('../data/deliveries.csv')
    runs = pd.read_csv('../data/IPL_runs_2008_2024.csv')
    wickets = pd.read_csv('../data/IPL_wickets_2024_wickets.csv')
    results = pd.read_csv('../data/IPL_Results(2008-2020).csv')
    return matches, deliveries, runs, wickets, results

def transform_data(matches, deliveries, runs, wickets, results):
    """Clean and transform datasets."""
    print("Transforming matches data...")

    # Clean team names (optional: if you still have full names)
    team_abbrev = {
        'Mumbai Indians': 'MI',
        'Chennai Super Kings': 'CSK',
        'Royal Challengers Bangalore': 'RCB',
        'Royal Challengers Bengaluru': 'RCB',
        'Kolkata Knight Riders': 'KKR',
        'Delhi Capitals': 'DC',
        'Delhi Daredevils': 'DC',  # older name for DC
        'Sunrisers Hyderabad': 'SRH',
        'Deccan Chargers': 'DCG',  # older team
        'Punjab Kings': 'PBKS',
        'Kings XI Punjab': 'PBKS',  
        'Rajasthan Royals': 'RR',
        'Gujarat Titans': 'GT',
        'Gujurat Lions' : 'GL',
        'Lucknow Super Giants': 'LSG',
        'Pune Warriors': 'PW',
        'Rising Pune Supergiants': 'RPS',
        'Rising Pune Supergiant': 'RPS',  # another variation
        'Gujarat Lions': 'GL',
        'Kochi Tuskers Kerala': 'KTK',
        'MUMBAI INDIANS': 'MI',
        'CHENNAI SUPER KINGS': 'CSK',
        'ROYAL CHALLENGERS BANGLORE': 'RCB',
        'ROYAL CHALLENGERS BENGALURU': 'RCB',
        'KOLKATA KNIGHT RIDERS': 'KKR',
        'DELHI CAPITALS': 'DC',
        'DELHI DAREDEVILS': 'DC',  # older name for DC
        'SUNRISERS HYDERABAD': 'SRH',
        'DECCAN CHARGERS': 'DCG',  # older team
        'PUNJAB KINGS': 'PBKS',
        'KINGS XI PUNJAB': 'PBKS',  
        'RAJASTHAN ROYALS': 'RR',
        'GUJURAT TITANS': 'GT',
        'GUJURAT LIONS' : 'GL',
        'LUCKNOW SUPER GIANTS': 'LSG',
        'PUNE WARRIORS': 'PW',
        'RISING PUNE SUPERGIANTS': 'RPS',
        'RISING PUNE SUPERGIANT': 'RPS',  # another variation
        'KOCHI TUSKERS KERALA': 'KTK'
    }
    
    #season-matches
    

    for col in ['team1', 'team2', 'toss_winner', 'winner']:
        if col in matches.columns:
            matches[col] = matches[col].astype(str).str.strip().replace(team_abbrev)

    matches.loc[matches['season'] == '2007/08', 'season'] = '2008'
    matches.loc[matches['season'] == '2009/10', 'season'] = '2010'
    matches.loc[matches['season'] == '2020/21', 'season'] = '2020'

    venue_mapping = {
        'MA Chidambaram Stadium, Chepauk': 'MA Chidambaram Stadium',
        'MA Chidambaram Stadium, Chennai': 'MA Chidambaram Stadium',
        'MA Chidambaram Stadium, Chepauk, Chennai': 'MA Chidambaram Stadium',

        'Wankhede Stadium, Mumbai': 'Wankhede Stadium',
        'Wankhede Stadium': 'Wankhede Stadium',

        'M Chinnaswamy Stadium': 'M Chinnaswamy Stadium',
        'M.Chinnaswamy Stadium': 'M Chinnaswamy Stadium',
        'M Chinnaswamy Stadium, Bengaluru': 'M Chinnaswamy Stadium',

        'Feroz Shah Kotla': 'Arun Jaitley Stadium',
        'Feroz Shah Kotla Ground': 'Arun Jaitley Stadium',
        'Arun Jaitley Stadium': 'Arun Jaitley Stadium',
        'Feroz Shah Kotla, Delhi': 'Arun Jaitley Stadium',
        'Arun Jaitley Stadium, Delhi': 'Arun Jaitley Stadium',
        'Punjab Cricket Association Stadium, Mohali': 'IS Bindra Stadium, Mohali',
        'Punjab Cricket Association IS Bindra Stadium, Mohali': 'IS Bindra Stadium, Mohali',

        'Sawai Mansingh Stadium, Jaipur': 'Sawai Mansingh Stadium',
        'Sawai Mansingh Stadium': 'Sawai Mansingh Stadium',

        'Narendra Modi Stadium, Ahmedabad': 'Narendra Modi Stadium',
        'Motera Stadium, Ahmedabad': 'Narendra Modi Stadium',

        'Rajiv Gandhi International Stadium, Uppal': 'Rajiv Gandhi International Stadium',
        'Rajiv Gandhi International Stadium, Hyderabad': 'Rajiv Gandhi International Stadium',

        'Dr DY Patil Sports Academy, Navi Mumbai': 'Dr DY Patil Stadium',
        'Dr DY Patil Sports Academy': 'Dr DY Patil Stadium',
        'Dr DY Patil Sports Academy, Mumbai' : 'Dr DY Patil Stadium',
        'Barabati Stadium, Cuttack': 'Barabati Stadium',
        'Holkar Cricket Stadium, Indore': 'Holkar Cricket Stadium',
        'Eden Gardens, Kolkata': 'Eden Gardens',
        'Brabourne Stadium, Mumbai': 'Brabourne Stadium'
    }

    # Apply standardization
    matches['venue'] = matches['venue'].replace(venue_mapping)

    #deliveries.csv
    for col in ['batting_team','bowling_team']:
        if col in deliveries.columns:
            deliveries[col] = deliveries[col].astype(str).str.strip().replace(team_abbrev)
    
    
    #results.csv
    for col in ['Team1','Team2']:
        if col in results.columns:
            results[col] = results[col].astype(str).str.strip().replace(team_abbrev)

    # Parse the Result column
    def parse_result(row):
        match = re.match(r"(.+?)\s+won by\s+(\d+)\s+(runs|wickets)", str(row))
        if match:
            return pd.Series({
                'winning_team': match.group(1),
                'win_margin': int(match.group(2)),
                'win_type': match.group(3)
            })
        else:
            return pd.Series({'winning_team': None, 'win_margin': None, 'win_type': None})

    parsed = matches['result'].apply(parse_result)
    matches = pd.concat([matches, parsed], axis=1)

    print("Transformation complete.")
    return matches, deliveries, runs, wickets, results

def load_data(matches, deliveries, runs, wickets, results):
    """Load all datasets into SQLite and backup CSVs."""
    if not os.path.exists('cleaned_data'):
        os.makedirs('cleaned_data')

    # Save CSVs
    matches.to_csv('cleaned_data/matches_cleaned.csv', index=False)
    deliveries.to_csv('cleaned_data/deliveries_cleaned.csv', index=False)
    runs.to_csv('cleaned_data/runs_cleaned.csv', index=False)
    wickets.to_csv('cleaned_data/wickets_cleaned.csv', index=False)
    results.to_csv('cleaned_data/results_cleaned.csv', index=False)

    # Save into SQLite
    conn = sqlite3.connect('ipl_data.db')
    matches.to_sql('matches', conn, if_exists='replace', index=False)
    deliveries.to_sql('deliveries', conn, if_exists='replace', index=False)
    runs.to_sql('runs', conn, if_exists='replace', index=False)
    wickets.to_sql('wickets', conn, if_exists='replace', index=False)
    results.to_sql('results', conn, if_exists='replace', index=False)
    conn.close()

    print("Data loaded into SQLite and CSVs saved.")

def etl_pipeline():
    """Run full ETL pipeline."""
    matches, deliveries, runs, wickets, results = extract_data()
    matches, deliveries, runs, wickets, results = transform_data(matches, deliveries, runs, wickets, results)
    load_data(matches, deliveries, runs, wickets, results)

if __name__ == "__main__":
    etl_pipeline()

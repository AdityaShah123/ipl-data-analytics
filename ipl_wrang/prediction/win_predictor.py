import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
from sklearn.linear_model import LogisticRegression

from sklearn.model_selection import train_test_split
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



def scrape_cricbuzz_ipl_2025_points():
    url = "https://www.cricbuzz.com/cricket-series/9237/indian-premier-league-2025/points-table"

    options = Options()
    options.add_argument("--headless")  
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    driver.get(url)
    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    tables = soup.find_all('table', {'class': 'table cb-srs-pnts'})
    print(soup)
    print(tables)
    if not tables:
        print("❌ No points table found.")
        return None

    table = tables[0]  

    teams = []
    matches_played = []
    wins = []
    losses = []
    ties = []
    points = []
    nrr = []

    for row in table.find('tbody').find_all('tr'):
        cols = row.find_all('td')

        if len(cols) >= 8 and not cols[0].text.strip().isdigit():
            team_name = cols[0].text.strip()

            try:
                played = int(cols[1].text.strip())
                win = int(cols[2].text.strip())
                loss = int(cols[3].text.strip())
                tie = int(cols[4].text.strip())
                no_result = int(cols[5].text.strip())
                team_points = int(cols[6].text.strip())
                net_rr = float(cols[7].text.strip())
            except ValueError:
                continue  # Skip bad rows

            teams.append(team_name)
            matches_played.append(played)
            wins.append(win)
            losses.append(loss)
            ties.append(tie)
            points.append(team_points)
            nrr.append(net_rr)

    df_points = pd.DataFrame({
        'team': teams,
        'matches_played': matches_played,
        'wins': wins,
        'losses': losses,
        'ties': ties,
        'points': points,
        'nrr': nrr
    })

    # Add win ratio (new feature!)
    df_points['win_ratio'] = df_points['wins'] / df_points['matches_played']

    return df_points

import pandas as pd

# Manually copied points table from Cricbuzz (April 28, 2025 snapshot)
data = {
    'team': [
        'Royal Challengers Bengaluru',
        'Mumbai Indians',
        'Gujarat Titans',
        'Delhi Capitals',
        'Punjab Kings',
        'Lucknow Super Giants',
        'Kolkata Knight Riders',
        'Rajasthan Royals',
        'Sunrisers Hyderabad',
        'Chennai Super Kings'
    ],
    'matches_played': [10, 10, 9, 10, 9, 10, 10, 10, 9, 9],
    'wins': [7, 6, 6, 6, 5, 5, 4, 3, 3, 2],
    'losses': [3, 4, 3, 4, 3, 5, 5, 7, 6, 7],
    'ties': [0] * 10,
    'points': [14, 12, 12, 12, 11, 10, 9, 6, 6, 4],
    'nrr': [0.521, 0.889, 0.748, 0.362, 0.177, -0.325, 0.080, -0.349, -1.103, -1.302]
}

# Create DataFrame
df_points = pd.DataFrame(data)

# Add win_ratio column
df_points['win_ratio'] = df_points['wins'] / df_points['matches_played']

# Preview
print(df_points)

# Optionally save to CSV if needed
# df_points.to_csv("ipl_2025_points_table.csv", index=False)

def build_historical_data():
    matches = pd.read_csv('/Users/Manan/Desktop/data_wranf_submission_folder/project-group-11/ipl_wrang/data/matches.csv')

    matches['season'] = matches['season'].astype(str)
    matches['season'] = matches['season'].replace({'2007/08': '2008', '2009/10': '2010', '2020/21': '2020'})

    played = matches.groupby(['season', 'team1']).size().reset_index(name='matches')
    played.rename(columns={'team1': 'team'}, inplace=True)

    wins = matches.groupby(['season', 'winner']).size().reset_index(name='wins')
    wins.rename(columns={'winner': 'team'}, inplace=True)

    team_stats = pd.merge(played, wins, on=['season', 'team'], how='left')
    team_stats['wins'] = team_stats['wins'].fillna(0)
    team_stats['win_ratio'] = team_stats['wins'] / team_stats['matches']

    champions = matches.dropna(subset=['winner']).groupby('season')['winner'].agg(lambda x: x.value_counts().idxmax()).reset_index()
    champions.rename(columns={'winner': 'champion_team'}, inplace=True)

    data = pd.merge(team_stats, champions, on='season', how='left')
    data['is_champion'] = (data['team'] == data['champion_team']).astype(int)

    return data


def train_model(data):
    X = data[['win_ratio']]
    y = data['is_champion']

    if y.sum() == 0:
        print(" No champion teams in training data.")
        return None

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, stratify=y)

    model = LogisticRegression()
    model.fit(X_train, y_train)

    return model



def predict_ipl_2025(model, df_points):
    X_pred = df_points[['win_ratio']]

    df_points['champion_prob'] = model.predict_proba(X_pred)[:, 1]

    df_points_sorted = df_points.sort_values(by='champion_prob', ascending=False)

    print(df_points_sorted[['team', 'champion_prob']])

    probable_winner = df_points_sorted.iloc[0]['team']
    print(f"\n Most likely IPL 2025 Winner: {probable_winner} ")

    return probable_winner


def main():
    print("Scraping IPL 2025 points table...")
    #df_points = scrape_cricbuzz_ipl_2025_points()
    print('Scraped Points Table:')
    print(df_points)

    if df_points is None or df_points.empty:
        print("Failed to scrape Points Table! Try again later.")
        return

    print("Building historical IPL data...")
    data = build_historical_data()

    print("Training model...")
    model = train_model(data)

    print("phase : Predicting IPL 2025 winner...")
    predict_ipl_2025(model, df_points)

if __name__ == "__main__":
    main()

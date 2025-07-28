import pytest
import pandas as pd

matches = pd.read_csv('../ingestion/cleaned_data/matches_cleaned.csv')

valid_teams = {
    'MI', 'CSK', 'RCB', 'KKR', 'DC', 'DD', 'SRH', 'DCG', 
    'PBKS', 'KXIP', 'RR', 'GT', 'LSG', 'PW', 'RPS', 'GL', 'KTK'
}

valid_toss_decisions = {'bat', 'field'}
valid_seasons = [str(year) for year in range(2008, 2025)]

def test_team_names():
    """Test that team1 and team2 are valid IPL teams."""
    teams1 = set(matches['team1'].dropna().unique())
    teams2 = set(matches['team2'].dropna().unique())
    toss_winner = set(matches['toss_winner'].dropna().unique())
    winner = set(matches['winner'].dropna().unique())

    assert teams1.issubset(valid_teams), f"Invalid team names found in team1: {teams1 - valid_teams}"
    assert teams2.issubset(valid_teams), f"Invalid team names found in team2: {teams2 - valid_teams}"
    assert toss_winner.issubset(valid_teams), f"Invalid team names found in toss_winner: {toss_winner - valid_teams}"
    assert winner.issubset(valid_teams), f"Invalid team names found in winner: {winner - valid_teams}"

def test_no_missing_match_id():
    """Test that there are no missing match ids."""
    assert matches['id'].isnull().sum() == 0, "Missing values found in match id."

def test_valid_season_years():
    """Test that seasons are within valid IPL years."""
    seasons = set(matches['season'].dropna().astype(str).unique())
    assert seasons.issubset(valid_seasons), f"Invalid seasons found: {seasons - set(valid_seasons)}"


def test_valid_toss_decision():
    """Test toss decision is either bat or field."""
    toss_decisions = set(matches['toss_decision'].dropna().str.lower().unique())
    assert toss_decisions.issubset(valid_toss_decisions), f"Invalid toss decisions found: {toss_decisions - valid_toss_decisions}"

def test_no_missing_values_important_cols():
    """Test important columns have no missing values."""
    important_cols = ['id', 'season', 'team1', 'team2', 'date']
    for col in important_cols:
        assert matches[col].isnull().sum() == 0, f"Missing values found in column {col}"

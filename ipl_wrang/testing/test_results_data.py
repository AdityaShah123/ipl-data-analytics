import pytest
import pandas as pd

results = pd.read_csv('../ingestion/cleaned_data/results_cleaned.csv')

valid_teams = {
    'MI', 'CSK', 'RCB', 'KKR', 'DC', 'DD', 'SRH', 'DCG',
    'PBKS', 'KXIP', 'RR', 'GT', 'LSG', 'PW', 'RPS', 'GL', 'KTK'
}

valid_results = {'normal', 'tie', 'no result'}
valid_years = {str(y) for y in range(2008, 2025)}


def test_no_missing_date():
    """Test that the Date column has no missing values."""
    assert results['Date'].isnull().sum() == 0, "Missing dates found in 'Date' column."


def test_valid_teams():
    """Ensure Team1 and Team2 are valid IPL teams."""
    team1 = set(results['Team1'].dropna().unique())
    team2 = set(results['Team2'].dropna().unique())
    assert team1.issubset(valid_teams), f"Invalid team names in Team1: {team1 - valid_teams}"
    assert team2.issubset(valid_teams), f"Invalid team names in Team2: {team2 - valid_teams}"


def test_no_missing_important_cols():
    """Check no missing values in critical columns."""
    important = ['Team1', 'Team2', 'Date', 'Year', 'Toss', 'TossDecision', 'Result']
    for col in important:
        assert results[col].isnull().sum() == 0, f"Missing values in column {col}"

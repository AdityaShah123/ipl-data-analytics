import pytest
import pandas as pd

deliveries = pd.read_csv('../ingestion/cleaned_data/deliveries_cleaned.csv')

valid_teams = {
    'MI', 'CSK', 'RCB', 'KKR', 'DC', 'DD', 'SRH', 'DCG', 
    'PBKS', 'KXIP', 'RR', 'GT', 'LSG', 'PW', 'RPS', 'GL', 'KTK'
}

valid_extras = {'wides', 'noballs', 'byes', 'legbyes', 'penalty'}

valid_dismissals = {
    'bowled', 'caught', 'lbw', 'run out', 'stumped', 
    'hit wicket', 'retired hurt', 'obstructing the field',
    'retired out', 'caught and bowled'
}


def test_valid_teams_present():
    """Test that all team names are from valid IPL franchises."""
    batting_teams = set(deliveries['batting_team'].dropna().unique())
    bowling_teams = set(deliveries['bowling_team'].dropna().unique())
    assert batting_teams.issubset(valid_teams), f"Invalid batting teams found: {batting_teams - valid_teams}"
    assert bowling_teams.issubset(valid_teams), f"Invalid bowling teams found: {bowling_teams - valid_teams}"

def test_inning_and_ball_ranges():
    """Test that innings are either 1 or 2 and ball values are in 1-6."""
    assert deliveries['inning'].between(1, 6).all(), "Invalid inning values found"
    assert deliveries['ball'].between(1, 11).all(), "Invalid ball values found"

def test_no_missing_in_essential_columns():
    """Ensure essential columns have no missing values."""
    essential_columns = [
        'match_id', 'inning', 'batting_team', 'bowling_team', 
        'over', 'ball', 'batter', 'bowler', 'non_striker', 
        'batsman_runs', 'extra_runs', 'total_runs', 'is_wicket'
    ]
    for col in essential_columns:
        assert deliveries[col].isnull().sum() == 0, f"Missing values found in column: {col}"

def test_extras_type_values():
    """Test that all extras_type values are valid if not null."""
    extras = set(deliveries['extras_type'].dropna().unique())
    assert extras.issubset(valid_extras), f"Invalid extras_type values found: {extras - valid_extras}"

def test_dismissal_types():
    """Ensure dismissal kinds are within valid types when not null."""
    dismissals = set(deliveries['dismissal_kind'].dropna().unique())
    assert dismissals.issubset(valid_dismissals), f"Invalid dismissal kinds found: {dismissals - valid_dismissals}"

def test_run_consistency():
    """Check if total_runs equals batsman_runs + extra_runs."""
    run_check = deliveries['total_runs'] == (deliveries['batsman_runs'] + deliveries['extra_runs'])
    assert run_check.all(), "Mismatch in run total computation"


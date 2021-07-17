from pathlib import Path

TEAM_ID = "1060762"
_TOTAL_CHEEMS = {
    range(1, 6): 7000,
    range(6, 11): 4000,
    range(11, 21): 3000,
    range(21, 36): 2000,
    range(36, 51): 1500,
    range(51, 71): 625
    # TODO: Handle when range is greater than this
}
# https://stackoverflow.com/a/57884712/13837629
TOTAL_CHEEMS = {num: value for rng, value in _TOTAL_CHEEMS.items() for num in rng}
MIN_CHEEMS = 3
RATE = 1 / 5000

# This is so it works wherever it's called
DATA_PATH = Path(__file__).parent / "../data"
PREVIOUS_PATH = DATA_PATH / "previous.json"
CSV_PATH = DATA_PATH / "payout.csv"
START_PATH = DATA_PATH / "start-date.txt"
TOKEN_PATH = DATA_PATH / "token.json"
CRED_PATH = DATA_PATH / "credentials.json"
WEEK_PATH = DATA_PATH / "week-num.txt"

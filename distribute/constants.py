from pathlib import Path

TEAM_ID = "1060762"
TOTAL_CHEEMS = 3000
MIN_CHEEMS = 3
RATE = 1 / 5000

# This is so it works wherever it's called
DATA_PATH = Path(__file__).parent / "../data"
PREVIOUS_PATH = DATA_PATH / "previous.json"
CSV_PATH = DATA_PATH / "payout.csv"
START_PATH = DATA_PATH / "start-date.txt"
TOKEN_PATH = DATA_PATH / "token.json"
CRED_PATH = DATA_PATH / "credentials.json"

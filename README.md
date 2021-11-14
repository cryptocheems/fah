# fah

Distribution script for Folding at Home for Cheemscoin

## How to Use

Note: These are the instructions for mac / linux. Windows may be slightly different.

### Initial Setup

1. Clone this repository onto your computer and open a terminal in the directory
2. `python3 -m venv venv`
3. `source venv/bin/activate` if using Bash or `source venv/bin/activate.fish` if using fish
4. `python -m pip install -r requirements.txt`

### Distribute Cheemscoin

1. `source venv/bin/activate` if using Bash or `source venv/bin/activate.fish` if using fish
2. `python distribute/fah.py`

### Update Dependency List

After you install any additional dependencies (while in the venv) you should update the dependency list with `pip freeze > requirements.txt`

## Troubleshooting

If you get the error `ValueError: {'code': -32010, 'message': 'Filtered'}` then check what the gas price is on https://blockscout.com/ and change it in `distribute/blockchain.py` to match or be higher.

## Cron job to run every Sunday

`0 12 * * 0 cd ~/fah; source venv/bin/activate; python distribute/fah.py`  
Note: I have found this doesn't work because the Google token isn't cached properly.

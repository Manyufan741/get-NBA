# get-NBA
This is the Capstone-1 project for Springboard Software Engineering Course.

Main API used: https://www.balldontlie.io/api/v1
API for image gathering: https://nba-players.herokuapp.com/

# User Flow
1. You'll need to sign up or log in to enjoy the features.
2. After logged in, users can click the "Player Career Stat Search" on the right side of the page to search for a player's career stat. Users will need provide the player's first and last name for the search.
3. Users can also do an advanced search by providing the name of the player, a time frame from start_date to end_date, and searching criteria on stats.
    For example:
    If you want to know the games' stats of "Allen Iverson" scoring more than or equal to 50 points between Feb 1, 2000 and June 30, 2008, you should enter "Allen" in the Player First Name field, "Iverson" in the Player Last Name field, "2000-2-1" in the Starting Date field, "2008-6-30" in the End Date field and "50" in the Points field.

# Developer notes
1. To create virtual environment: python -m venv venv
2. To activate virtual environmet: source venv/bin(or Scripts)/activate
3. To install required dependencies in virtual environment: pip install requirements.txt
4. To preload the database of top 5 players: python nba_core/scripts/top5.py
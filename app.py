import streamlit as st
import json
import os
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.image as mpimg

# Title of the app
st.title("Football Player Heatmap Visualization")

# Step 1: Set up paths for match data and structured data (relative or absolute paths)
match_ids = ['2068','2269','2417','2440','2841','3442','3518','3749','4039']
team  = { 
    "id":["145","139"] , "team":["Inter","Juve"]
}
# Function to load JSON files
def load_json(filepath):
    with open(filepath, 'r') as file:
        return json.load(file)


# Dictionary to store the match data
match_data_scores = {}

# Load and extract relevant information from match JSON files
for match_id in match_ids:
    data_dir = os.path.join(os.getcwd(),'data', 'matches', match_id)
    match_json_path = os.path.join(data_dir, 'match_data.json')
    match_data = load_json(match_json_path)
    
    # Extract home and away team names and the score
    home_team_name = match_data['home_team']['name']
    away_team_name = match_data['away_team']['name']
    home_team_score = match_data['home_team_score']
    away_team_score = match_data['away_team_score']
    
    # Store the data in a dictionary with match ID as the key
    match_data_scores[match_id] = {
        'home_team': home_team_name,
        'away_team': away_team_name,
        'home_team_score': home_team_score,
        'away_team_score': away_team_score
    }

# Create the dropdown list using the format "Home Team vs Away Team"
matches = {match_id: f"{match_data_scores[match_id]['home_team']} vs {match_data_scores[match_id]['away_team']}" 
           for match_id in match_ids}

# Step 2: Select a match based on "Home Team vs Away Team"
selected_match = st.sidebar.selectbox("Select Match", list(matches.values()))

# Find the selected match ID based on the match name chosen
selected_match_id = [match_id for match_id, match_name in matches.items() if match_name == selected_match][0]

# Display the selected match details
selected_match_data = match_data_scores[selected_match_id]
st.write(f"Selected Match: {selected_match_data['home_team']} {selected_match_data['home_team_score']} - "
         f"{selected_match_data['away_team_score']} {selected_match_data['away_team']}")

# Step 3: Load match data for the selected match ID
data_dir = os.path.join(os.getcwd(), 'data', 'matches', selected_match_id)
match_data = load_json(os.path.join(data_dir, 'match_data.json'))
structured_data = load_json(os.path.join(data_dir, 'structured_data.json'))
# determine home team and away team id 
home_team_id = match_data['home_team']['id']
away_team_id = match_data['away_team']['id']

for player in match_data['players']:
    if player['team_id'] == home_team_id:
        player['team_id'] = match_data['home_team']['short_name']
    elif player['team_id'] == away_team_id:
        player['team_id'] = match_data['away_team']['short_name']

# Step 3: Create a mapping for players (trackable_object to player name)
players = {player['trackable_object']: f"{player['first_name']} {player['last_name']} (Team {player['team_id']})" 
           for player in match_data['players']}

# Step 5: Select a player from the sidebar
st.sidebar.header("Select Options")
selected_player_id = st.sidebar.selectbox("Select Player", list(players.keys()), format_func=lambda x: players[x])

# Step 6: Extract tracking data for the selected player, separated by period
player_positions = {
    'period_1': {'x': [], 'y': []},
    'period_2': {'x': [], 'y': []}
}
for possession in structured_data:
    for obj in possession['data']:
        if obj.get('trackable_object') == selected_player_id:
            if possession['period'] == 1:
                player_positions['period_1']['x'].append(obj['x'])
                player_positions['period_1']['y'].append(obj['y'])
            elif possession['period'] == 2:
                player_positions['period_2']['x'].append(obj['x'])
                player_positions['period_2']['y'].append(obj['y'])

# Step 7: Load the football pitch image
pitch_img = mpimg.imread('pitch.png')

# Step 8: Generate heatmap for each period
for period, positions in player_positions.items():
    if len(positions['x']) == 0 or len(positions['y']) == 0:
        st.write(f"No tracking data found for {period.replace('_', ' ')} for the selected player.")
        continue

    # Plot heatmap with the football pitch background
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Display the pitch image
    ax.imshow(pitch_img, extent=[-52.5, 52.5, -34, 34], aspect='auto')

    # Overlay the heatmap
    sns.kdeplot(x=positions['x'], y=positions['y'], shade=True, cmap="Reds", alpha=0.5, ax=ax)

    player_name = players[selected_player_id]
    ax.set_title(f"Heatmap for {player_name} - {period.replace('_', ' ').title()}")
    ax.set_xlabel('X Coordinate (meters)')
    ax.set_ylabel('Y Coordinate (meters)')

    # Set pitch boundaries according to a standard football field size
    ax.set_xlim([-52.5, 52.5])  # Half-length of a standard football field (105m)
    ax.set_ylim([-34, 34])      # Half-width of a standard football field (68m)

    # Display the heatmap in Streamlit
    st.pyplot(fig)

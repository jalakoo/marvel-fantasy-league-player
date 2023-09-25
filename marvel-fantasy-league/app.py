import streamlit as st
from logic import get_active_tournaments, get_teams_for, add_team, get_characters, get_characters_on_team, delete_team, update_team_characters, ready_to_play


# Setup
USER = "current_user"
if USER not in st.session_state:
    st.session_state[USER] = ""
TOURNAMENT = "selected_tournament"
if TOURNAMENT not in st.session_state:
     st.session_state[TOURNAMENT] = ""
TEAM = "current_team"
if TEAM not in st.session_state:
    st.session_state[TEAM] = ""


st.title('Marvel Fantasy League')

# TODO: proper email validation
email = st.text_input("Email")
email = email.lower()

st.session_state[USER] = email

if st.session_state[USER] == "":
    st.write('Please add an email to start playing')
    st.stop()

# Tournaments
tournament_names = get_active_tournaments()
selected_tournament = st.selectbox(
    'Select a Tournament to Join',
    tournament_names
)
if selected_tournament is None or selected_tournament == "":
    st.stop()
st.session_state[TOURNAMENT] = selected_tournament

# Team
user_teams = get_teams_for(st.session_state[USER])

# Existing Teams
if len(user_teams) > 0:
    st.write('Your Team(s):')
for team in user_teams:
    # Generate a row of team expandable options
    with st.expander(team):
        all_characters = get_characters()
        team_characters = get_characters_on_team(team, st.session_state[USER])
        selected_characters = st.multiselect(
            "Select your team members",
            all_characters,
            team_characters,
            max_selections=5
        )
        o1, o2, o3 = st.columns(3)

        # Update button
        with o1:
            if st.button('Save Team', key=f'{team}_update_button'):
                success, msg = update_team_characters(selected_characters, team, st.session_state[USER])
                if msg is not None:
                    st.error(msg)
                else:
                    st.success('Updated Team Makeup')
                    st.experimental_rerun()
        
        # Ready Button
        with o2:
            if st.button('Ready To Play', key=f'{team}_ready_to_play_button'):
                success, msg = ready_to_play(team, st.session_state[USER])
                if msg is not None:
                    st.error(msg)
                else:
                    st.success(f'{team} is ready for the tournament to start!')

        # Delete team button
        with o3:
            if st.button('Delete Team', key=f'{team}_delete_button'):
                success, msg = delete_team(team, st.session_state[USER])
                if msg is not None:
                    st.error(msg)
                else:
                    st.success(f'{team} deleted')
                    st.experimental_rerun()
# New Team(s)
if len(user_teams) == 0:
    new_team = st.text_input('Create New Team')
    if new_team != "":
        success, message = add_team(
            tournament = st.session_state[TOURNAMENT],
            team=new_team, 
            email = st.session_state[USER])
        if message is not None:
            st.error(message)
        else:
            st.success('New Team added')
            st.experimental_rerun()
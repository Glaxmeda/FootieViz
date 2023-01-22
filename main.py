# This is a sample Python script.
# This is a sample Python script.
import redis
import understatapi
import pickle
import streamlit as st
import pandas as pd
from scipy import stats


st.set_page_config(layout="wide", page_title="PL players test", page_icon=":PL:")

#Declare RedisStore
rd = redis.Redis(host="localhost", port=6379, db=0)

#Understat client + get PL players
understat = understatapi.UnderstatClient()
league_player_data = understat.league(league="EPL").get_player_data(season="2022")
players = pickle.dumps(league_player_data)
rd.set("Players",players)

@st.experimental_singleton
def load_data():
    players = pickle.loads(rd.get("Players"))
    return pd.DataFrame(players)

@st.experimental_memo
def get_player(data, name: str):
    name = name
    df1 = data.query("player_name == @name")
    df2 = df1.iloc[:, 4:].drop(columns=["yellow_cards", "red_cards", "position", "team_title"])
    df2 = df2.apply(pd.to_numeric)
    df3 = df2.div(data.time.apply(pd.to_numeric)/90,axis=0)
    return df3

data = load_data()
# LAYING OUT THE TOP SECTION OF THE APP
row1_1, row1_2 = st.columns((2, 3))

# SEE IF THERE'S A QUERY PARAM IN THE URL (e.g. ?pickup_hour=2)
# THIS ALLOWS YOU TO PASS A STATEFUL URL TO SOMEONE WITH A SPECIFIC HOUR SELECTED,
# E.G. https://share.streamlit.io/streamlit/demo-uber-nyc-pickups/main?pickup_hour=2
if not st.session_state.get("url_synced", False):
    try:
        pickup_hour = int(st.experimental_get_query_params()["player_name"][0])
        st.session_state["player_name"] = pickup_hour
        st.session_state["url_synced"] = True
    except KeyError:
        pass

# IF THE SLIDER CHANGES, UPDATE THE QUERY PARAM
def update_query_params():
    hour_selected = st.session_state["player_name"]
    st.experimental_set_query_params(player_name=hour_selected)


with row1_1:
    st.title("Understat Visualizer")
    player_name = st.selectbox(
        "Enter player name: ", options=data["player_name"], key="player_name", on_change=update_query_params
    )


with row1_2:
    st.write(
        """
    ##
    A tool for easy visual analysis
    """
    )

row2_1, row2_2, row2_3, row2_4 = st.columns((2, 1, 1, 1))

# with row2_1:
#     st.
with row2_2:
    st.write(player_name + " PL 22/23")
    df3['xG_rank'] = df3['xG'].rank(pct=True)
    st.bar_chart(data=get_player(data,player_name),y=list(data.columns))
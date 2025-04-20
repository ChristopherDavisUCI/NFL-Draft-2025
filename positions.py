import streamlit as st
import altair as alt
import pandas as pd
import numpy as np

st.set_page_config(layout="wide", page_title="2025 NFL Draft Positions")

st.title('2025 NFL Draft')

df = pd.read_csv("data/draft2025_streamlit.csv")
df["date"] = pd.to_datetime(df["date"])

# The following shouldn't be necessary unless a huge number of mocks are included.
alt.data_transformers.enable('default', max_rows = 50000)

def get_rank(df_mini, player):
    try:
        return list(df_mini["player"]).index(player)+1
    except:
        return None

# option can be "position" or "conference"
def make_chart(pos, df, option="position"):
    dfpos = df[df[option] == pos].copy()
    players = dfpos.player.unique()
    df_list = []
    for _, df_mini in dfpos.groupby("url", sort=None):
        row = df_mini.iloc[0]
        sample = {}
        for key in ["source", "date", "author", "url", "position", "draft-id"]:
            sample[key] = row[key]
        df_mini["rank"] = df_mini["player"].map(lambda player: get_rank(df_mini, player))
        mini_players = df_mini["player"].unique()
        for player in players:
            if player not in mini_players:
                new_row = sample.copy()
                new_row["player"] = player
                df_mini = pd.concat([df_mini, pd.DataFrame([new_row])])
        df_mini["count"] = len(mini_players)
        df_list.append(df_mini)
    df_rank = pd.concat(df_list, axis=0)
    base = alt.Chart(df_rank).encode(
        x=alt.X("draft-id:N", 
                axis=alt.Axis(
                    labelAngle=-55, 
                    labelLimit=200, 
                    labelOverlap=False, 
                    tickCount=200,
                    labelExpr="split(datum.value, '!')[0]",
                    #ticks=True,
                    grid=True
                    ), 
                sort=None),
        tooltip = ["player", "pick", "position", "team", "source", "author", "date"],
        href = "url:N"
    )

    points = base.mark_line(point=True).encode(
        y=alt.Y("pick:Q", scale=alt.Scale(reverse=True)),
        color=alt.Color(
            "player:N", 
            sort=None, 
            legend=alt.Legend(orient="left"),
            scale=alt.Scale(scheme="tableau20")
        ),
    )

    text = base.mark_text().encode(
        y = alt.value(-10),
        text = "count"
    )

    chart = points+text
    chart = chart.properties(
        title=pos,
        height=500,
    )
    return chart


# A few positions are missing
positions = [pos for pos in df["position"].unique() if isinstance(pos, str)]
conferences = sorted([conf for conf in df["conference"].unique() if isinstance(conf, str)])
authors = sorted(df["author"].unique())

# default_authors = sorted(list(df[df["date"].dt.month >= 3]["author"].unique()))

default_authors = ["Andy Molitor", "Charlie Campbell", "Dane Brugler", "Daniel Jeremiah",  
                   "Matthew Freedman",     
                  "Walter Cherepinsky", "Trevor Sikkema", "Rob Staton", "Jeff Risdon", ]
# yet to come "Peter Schrager", "Danny Kelly", "Benjamin Solak", 

chosen_authors = st.multiselect(
    "Choose your authors", 
    options = authors, 
    default = default_authors # default_authors when there are more
)

st.header("Positions")

pos = st.radio("What position?", positions, index = positions.index("QB"))

st.altair_chart(make_chart(pos, df[df["author"].isin(chosen_authors)]))

st.header("Conferences")

conf = st.radio("What conference?", conferences)

st.altair_chart(make_chart(conf, df[df["author"].isin(chosen_authors)], option="conference"))

# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
#     comment_magics: true
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.14.5
#   kernelspec:
#     display_name: discovery_climate_music_analysis
#     language: python
#     name: discovery_climate_music_analysis
# ---

# %% [markdown]
# # Chart Analysis

# %%
import numpy as np
import pandas as pd
import altair as alt
import configparser
from pathlib import Path
from tempfile import TemporaryDirectory

from pprint import pprint
from dateutil.parser import parse

from discovery_climate_music_analysis.getters.collect_songs import create_dataframe
from jacc_hammer.fuzzy_hash import Cos_config, Fuzzy_config, match_names_stream

USERNAME = "addie234"
PLAYLIST_ID = "spotify:playlist:4EhBYkl4jtI2POrkUxU6Ul"

# %%
# read chart data
all_top_charts = pd.read_csv("output.csv", header=None)
all_top_charts.columns = ["week_start", "chart_pos", "artist", "song"]
all_top_charts.reset_index(drop=True, inplace=True)

# %%
# climate songs dataframe
spotify_df_ = create_dataframe(USERNAME, PLAYLIST_ID)

# %% [markdown]
# ## Have any of our songs charted?

# %%
# set up for fuzzy matching
threshold = 0.3
chunksize = 100_000

cos_config = Cos_config()
fuzzy_config = Fuzzy_config()

tmp_dir = Path(TemporaryDirectory().name)
tmp_dir.mkdir()

# %%
# song plus artist for both lists

# x
list_of_chart_songs = (all_top_charts["song"] + " " + all_top_charts["artist"]).values
# y
list_of_spotify_songs = (spotify_df_["name"] + " " + spotify_df_["artist"]).values

# %%
# Calculate matches
output = match_names_stream(
    [list_of_chart_songs, list_of_spotify_songs],
    threshold=threshold,
    chunksize=chunksize,
    tmp_dir=tmp_dir,
    cos_config=cos_config,
    fuzzy_config=fuzzy_config,
)


# %%
def get_top_matches(df: pd.DataFrame) -> pd.DataFrame:
    """For each y get the x and sim_mean corresponding to highest sim_mean."""
    return df.loc[df.groupby("y").sim_mean.idxmax()]


# %%
top_matches = get_top_matches(pd.concat(output))

# %%
threshold = 75
chosen_top_matches = top_matches[top_matches["sim_mean"] > threshold]

# %%
print(list_of_chart_songs[136965])
print(list_of_spotify_songs[21])

# %%
match_single = all_top_charts.iloc[chosen_top_matches["x"].values.tolist(), :]
chart_info = match_single.apply(
    lambda y: all_top_charts[
        (all_top_charts["artist"] == y["artist"])
        & (all_top_charts["song"] == y["song"])
    ][["week_start", "chart_pos"]].to_dict("records"),
    axis=1,
)

# %%
spotify_w_chart_match = pd.concat(
    [spotify_df_, chosen_top_matches.set_index("y")], axis=1
)
spotify_w_chart_match_ = spotify_w_chart_match[
    ~spotify_w_chart_match["x"].isnull()
].reset_index(drop=True)
spotify_w_chart_match_["x"] = spotify_w_chart_match_["x"].astype(int)
spotify_w_chart_match_ = spotify_w_chart_match_.merge(
    chart_info.to_frame().reset_index(), left_on="x", right_on="index", how="left"
)
spotify_w_chart_match_.rename(columns={0: "chart_data"}, inplace=True)

# %% [markdown]
# ratio of songs (based on release dates) that have charted in the UK Top 100 official charts

# %%
spotify_w_chart_match["charted?"] = spotify_w_chart_match["x"].apply(
    lambda x: "y" if pd.notnull(x) else "n"
)

alt.Chart(spotify_w_chart_match).properties(width=250, height=300).mark_bar().encode(
    x="release_decade:O", y="count():Q", color="charted?"
)

# %% [markdown]
# Unique of occurence of CC songs charting in a decade (if a song charted in more then one decade, each decade is accounted for)

# %%
# explode chart info to rows

exploded = spotify_w_chart_match_.explode("chart_data").reset_index(drop=True)
songs_charted_ = exploded.join(pd.json_normalize(exploded["chart_data"]))

# extract year from chart info
songs_charted_["chart_year"] = songs_charted_["week_start"].apply(
    lambda x: parse(x, fuzzy=True).year
)

# grab highest chart position for song each year
songs_charted_ = (
    songs_charted_.sort_values("chart_pos")
    .drop_duplicates(["name", "artist", "release_date", "chart_year"], keep="first")
    .sort_index()
    .reset_index(drop=True)
)

songs_charted_["chart_decade"] = songs_charted_["chart_year"].apply(
    lambda x: x - (x % 10)
)

# %%
# drop songs that charted multiple times in same decade

songs_charted_unique = songs_charted_.drop_duplicates(
    subset=["name", "artist", "chart_decade"], keep="first"
)

# %%
# per decade
alt.Chart(songs_charted_unique).properties(width=250, height=300).mark_bar().encode(
    x="chart_decade:O", y="count():Q"
)

# %% [markdown]
# Scatter plot of songs charted

# %%
scatter_chart = (
    alt.Chart(songs_charted_)
    .properties(width=550, height=400)
    .transform_calculate(cat="datum.name + '-' + datum.artist")
    .mark_circle()
    .encode(
        x="chart_year:O",
        y=alt.Y("chart_pos", scale=alt.Scale(reverse=True)),
        color="name",
        tooltip=["name", "artist", "chart_pos", "chart_year", "release_date"],
    )
)

# marks = line_chart.mark_point(color='#333').encode(tooltip=['name', 'artist', 'chart_pos', 'chart_year', 'release_date'])

scatter_chart

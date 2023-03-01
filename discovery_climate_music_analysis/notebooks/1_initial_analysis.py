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
# # Initial Analysis

# %%
import numpy as np
import pandas as pd
import altair as alt

from discovery_climate_music_analysis.getters.collect_songs import create_dataframe

USERNAME = "addie234"
PLAYLIST_ID = "spotify:playlist:4EhBYkl4jtI2POrkUxU6Ul"

# %%
spotify_df_ = create_dataframe(USERNAME, PLAYLIST_ID)

# %% [markdown]
# Number of songs released each year

# %%
spotify_df_2 = (
    spotify_df_.copy()
    .groupby("release_year", as_index=False)
    .agg(no_of_songs=("name", "count"))
    .assign(timestamp=lambda df: pd.to_datetime(df.release_year.astype(str)))
    .assign(release_year=lambda df: df.release_year.astype(int))
    .fillna(0)
)
spotify_df_2["t"] = spotify_df_2["timestamp"].apply(lambda d: d.timestamp())
a = (
    alt.Chart(spotify_df_2)
    .mark_bar()
    .encode(
        x="year(timestamp):T", y=alt.Y("no_of_songs:Q", scale=alt.Scale(domain=[0, 12]))
    )
)

b = (
    alt.Chart(spotify_df_2)
    .mark_line()
    .encode(
        x=alt.X(
            "t",
            title=None,
            axis=alt.Axis(labels=False, ticks=False),
            scale=alt.Scale(nice=False),
        ),
        y=alt.Y("no_of_songs:Q", scale=alt.Scale(domain=[0, 12])),
    )
)

(
    a
    + b.transform_loess("t", "no_of_songs", bandwidth=0.1125).mark_line(
        size=4, color="red"
    )
).properties(width=700, height=250)


# %% [markdown]
# Number of songs released each decade

# %%
# per decade
alt.Chart(spotify_df_).properties(width=250, height=300).mark_bar().encode(
    x="release_decade:O", y=alt.Y("count():Q", scale=alt.Scale(domain=[0, 55]))
)

# %% [markdown]
# Popularity now

# %%
alt.Chart(
    spotify_df_,
).mark_bar().encode(
    y=alt.Y("name", sort="-x"),
    x=alt.X("popularity:Q"),
    color=alt.Color("popularity:Q"),
    tooltip=["name", "artist", "popularity"],
).transform_window(
    rank="rank(popularity)", sort=[alt.SortField("popularity", order="descending")]
).transform_filter(
    (alt.datum.rank < 20)
).configure_axis(
    labelLimit=1000
)

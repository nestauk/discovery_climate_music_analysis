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
# # Spotify Music Feature Analysis

# %%
# %load_ext autoreload
# %autoreload 2

import numpy as np
import pandas as pd
import altair as alt
import configparser
from pathlib import Path
from tempfile import TemporaryDirectory

from discovery_climate_music_analysis.getters.collect_songs import (
    create_dataframe,
    create_multi_playlist_dataframe,
)

BASELINE_USERNAME = "spotify"
USERNAME = "addie234"
PLAYLIST_ID = "spotify:playlist:4EhBYkl4jtI2POrkUxU6Ul"

# %%
# Collect songs of interest
spotify_df_ = create_dataframe(USERNAME, PLAYLIST_ID)

# %% [markdown]
# ## Against the baseline

# %% [markdown]
# 60s -> https://open.spotify.com/playlist/37i9dQZF1DXaKIA8E7WcJj?si=32e353bf261f4f7b
#
# 70s -> https://open.spotify.com/playlist/37i9dQZF1DWTJ7xPn4vNaz?si=15610d383c124776
#
# 80s -> https://open.spotify.com/playlist/37i9dQZF1DX4UtSsGT1Sbe?si=c36ce329dabe4762
#
# 90s -> https://open.spotify.com/playlist/37i9dQZF1DXbTxeAdrVG2l?si=bfbffc763b8a4066
#
# 00s -> https://open.spotify.com/playlist/37i9dQZF1DX4o1oenSJRJd?si=9856ae6b0ad84350
#
# 10s -> https://open.spotify.com/playlist/37i9dQZF1DX5Ejj0EkURtP?si=f843b25f888e4b0f
#
# 20s -> Only few years in!
# https://open.spotify.com/playlist/37i9dQZF1DX7Jl5KP2eZaS?si=32b7eae081c4462e
#
# https://open.spotify.com/playlist/37i9dQZF1DX18jTM2l2fJY?si=c91cd60bd31549af

# %%
baseline_dict = {
    "spotify:playlist:37i9dQZF1DXaKIA8E7WcJj": BASELINE_USERNAME,
    "spotify:playlist:37i9dQZF1DWTJ7xPn4vNaz": BASELINE_USERNAME,
    "spotify:playlist:37i9dQZF1DX4UtSsGT1Sbe": BASELINE_USERNAME,
    "spotify:playlist:37i9dQZF1DXbTxeAdrVG2l": BASELINE_USERNAME,
    "spotify:playlist:37i9dQZF1DX4o1oenSJRJd": BASELINE_USERNAME,
    "spotify:playlist:37i9dQZF1DX5Ejj0EkURtP": BASELINE_USERNAME,
    "spotify:playlist:37i9dQZF1DX7Jl5KP2eZaS": BASELINE_USERNAME,
    "spotify:playlist:37i9dQZF1DX18jTM2l2fJY": BASELINE_USERNAME,
}

# %%
baseline_df = create_multi_playlist_dataframe(baseline_dict)

# %% [markdown]
# VALENCE - Measure of happiness of songs v.s. baseline

# %%
box_val = (
    alt.Chart(spotify_df_)
    .mark_boxplot(size=50, extent=0.5, outliers={"size": 5})
    .encode(
        x="release_decade:O",
        y=alt.Y("valence:Q", scale=alt.Scale(zero=False)),
        color=alt.Color("release_decade:O", scale=alt.Scale(scheme="browns")),
        opacity=alt.value(0.8),
    )
    .properties(width=400)
)

baseline_val = (
    alt.Chart(baseline_df)
    .mark_line(strokeDash=[5, 5])
    .encode(
        x="release_decade:O",
        y=alt.Y("mean(valence):Q", scale=alt.Scale(zero=False)),
        color=alt.value("black"),
    )
    .properties(width=400)
)

cc_val = (
    alt.Chart(spotify_df_)
    .mark_line()
    .encode(
        x="release_decade:O",
        y=alt.Y("mean(valence):Q", scale=alt.Scale(zero=False)),
        tooltip=["mean(valence)"],
        color=alt.value("blue"),
    )
    .properties(width=400)
)

box_val + baseline_val + cc_val

# %% [markdown]
# DANCEABILITY - Measure of danceability of songs v.s. baseline

# %%
box_danceability = (
    alt.Chart(spotify_df_)
    .mark_boxplot(size=50, extent=0.5, outliers={"size": 5})
    .encode(
        x="release_decade:O",
        y=alt.Y("danceability:Q", scale=alt.Scale(zero=False)),
        color=alt.Color("release_decade:O", scale=alt.Scale(scheme="browns")),
        opacity=alt.value(0.8),
    )
    .properties(width=400)
)

baseline_dance = (
    alt.Chart(baseline_df)
    .mark_line(strokeDash=[5, 5])
    .encode(
        x="release_decade:O",
        y=alt.Y("mean(danceability):Q", scale=alt.Scale(zero=False)),
        color=alt.value("black"),
    )
    .properties(width=400)
)

cc_dance = (
    alt.Chart(spotify_df_)
    .mark_line()
    .encode(
        x="release_decade:O",
        y=alt.Y("mean(danceability):Q", scale=alt.Scale(zero=False)),
        color=alt.value("blue"),
    )
    .properties(width=400)
)

box_danceability + baseline_dance + cc_dance

# %% [markdown]
# ENERGY - Measure of energy of songs v.s. baseline

# %%
box_energy = (
    alt.Chart(spotify_df_)
    .mark_boxplot(size=50, extent=0.5, outliers={"size": 5})
    .encode(
        x="release_decade:O",
        y=alt.Y("energy:Q", scale=alt.Scale(zero=False)),
        color=alt.Color("release_decade:O", scale=alt.Scale(scheme="browns")),
        opacity=alt.value(0.8),
    )
    .properties(width=400)
)

baseline_energy = (
    alt.Chart(baseline_df)
    .mark_line(strokeDash=[5, 5])
    .encode(
        x="release_decade:O",
        y=alt.Y("mean(energy):Q", scale=alt.Scale(zero=False)),
        color=alt.value("black"),
    )
    .properties(width=400)
)

cc_energy = (
    alt.Chart(spotify_df_)
    .mark_line()
    .encode(
        x="release_decade:O",
        y=alt.Y("mean(energy):Q", scale=alt.Scale(zero=False)),
        color=alt.value("blue"),
    )
    .properties(width=400)
)

box_energy + baseline_energy + cc_energy

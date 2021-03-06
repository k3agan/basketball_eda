
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import base64
import pandas as pd
import streamlit as st
from re import S

st.title('NBA Stats Explorer')

st.markdown("""
This app does some simple webscraping of NBA player stats data
* **Python libraries:** base64, pandas, streamlit
* **Data source** [Basketball-reference.com](https://www.basketball-reference.com/).
""")

st.sidebar.header('user input features')
selected_year = st.sidebar.selectbox('year', list(reversed(range(1950, 2020))))

# web scarping part

# @st.cache


@st.cache
def load_data(year):
    url = "https://www.basketball-reference.com/leagues/NBA_" + \
        str(year) + "_per_game.html"
    html = pd.read_html(url, header=0)
    df = html[0]
    raw = df.drop(df[df.Age == 'Age'].index)  # delete header in content
    raw = raw.fillna(0)
    playerstats = raw.drop(['Rk'], axis=1)
    return playerstats


playerstats = load_data(selected_year)

# sidebar - select team
sorted_unique_team = sorted(playerstats.Tm.unique())
selected_team = st.sidebar.multiselect(
    'Team', sorted_unique_team, sorted_unique_team)

# sidebar - position selection
unique_pos = ['C', 'PF', 'SF', 'PG', 'SG']
selected_pos = st.sidebar.multiselect('Position', unique_pos, unique_pos)

# filter data
df_selected_team = playerstats[
    (playerstats.Tm.isin(selected_team)) &
    (playerstats.Pos.isin(selected_pos))]

st.header('Display player stats of selected Team(s)')
st.write('Data Dimension: ' + str(df_selected_team.shape[0]) + ' rows and ' + str(
    df_selected_team.shape[1]) + ' columns.')
st.dataframe(df_selected_team)

# Download nba player stats data
# https://discuss.streamlit.io/t/how-to-download-file-in-streamlit/1806


def filedownload(df):
    csv = df.to_csv(index=False)
    # strings <-> bytes conversions
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="playerstats.csv">Download CSV File</a>'
    return href


st.markdown(filedownload(df_selected_team), unsafe_allow_html=True)

# Heatmap
if st.button('Intercorrelation Heatmap'):
    st.header('Intercorrelation matrix heatmap')
    df_selected_team.to_csv('output.csv', index=False)
    df = pd.read_csv('output.csv')

    corr = df.corr()
    mask = np.zeros_like(corr)
    mask[np.triu_indices_from(mask)] = True
    with sns.axes_style("white"):
        f, ax = plt.subplots(figsize=(7, 5))
        ax = sns.heatmap(corr, mask=mask, vmax=1, square=True)
    st.pyplot(f)

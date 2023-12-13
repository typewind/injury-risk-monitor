import streamlit as st
import altair as alt
import matplotlib.pyplot as plt
from matplotlib import rc
import pandas as pd


import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from pre_process import task1_clean_data, info_box, RTP_THRESHOLD, IMBALANCE, draw_alt, load_comment, submit_comment

# matplotlib setting
font = {'size': 8
        }

rc('font', **font)

# Get data
df1 = task1_clean_data()
comment_table = load_comment()

# dashboard layout config
st.set_page_config(layout="wide")


# title
st.title("Hamstring Strength and Imbalance Risk Dashboard")


with st.sidebar:
    st.subheader("Filter")
    option_age_group = st.multiselect(
        "Age Group",
        df1["Age Group"].sort_values().unique(),
        ["1st Team F", "1st Team M"]
    )
    option_status = st.multiselect(
        'Status',
        df1["Status"].unique(),
        ['Active']
    )
    rtp_lvl = st.slider("How many metrics to be recovered?*", 
                        0, 8, (0, 8))
        
    is_imba = st.multiselect("Is player imbalance?*",
                             df1["L/R Imbalance"].unique(),
                             df1["L/R Imbalance"].unique()
                             )
    st.markdown("---")


# L Max Force


# range=["#e7ba52", "#a7a7a7", "#aec7e8", "#1f77b4", "#9467bd"],


df1_filtered = df1[(df1["Status"].isin(option_status)) &
                   (df1["RTP Level"] >= rtp_lvl[0]) &
                   (df1["RTP Level"] <= rtp_lvl[1]) &
                   (df1["L/R Imbalance"].isin(is_imba) &
                    (df1["Age Group"].isin(option_age_group))
                    )
                   ]

# to show the traffic light
df_latest = df1.sort_values("Datetime UTC").groupby("Player ID").tail(1)
df_latest = df_latest[(df_latest["Status"].isin(option_status)) &
                   (df_latest["RTP Level"] >= rtp_lvl[0]) &
                   (df_latest["RTP Level"] <= rtp_lvl[1]) &
                   (df_latest["L/R Imbalance"].isin(is_imba) &
                    (df_latest["Age Group"].isin(option_age_group))
                    )
                   ]


with st.sidebar:
    option_player = st.selectbox(
    label = "Player ID",
    options = df_latest["Player ID"].sort_values().unique()
    )

df_player = df1[(df1["Player ID"]==option_player) ].sort_values(by="Datetime UTC")

with st.sidebar:
    # init session
    option_test = st.selectbox(
        'Test',
        df1[(df1["Player ID"]==option_player)].dropna()["Test"].unique().tolist()
    )

df_player = df_player[(df_player["Test"]==option_test) ]
df_latest_player = df_latest[(df_latest["Player ID"]==option_player)&
                                    (df_latest["Test"]==option_test) ]

# info box
total_players, imba, no_rtp= st.columns(3)
with total_players:
    st.markdown(info_box(sline="Total Players Selected",
                        iconname = "fas fa-users",
                        color_box = (24, 116, 152),
                        i=len(df_latest["Player ID"].unique())
                        ),
            unsafe_allow_html=True)
with imba:
    st.markdown(info_box(sline="Imbalance",
                         iconname = "fas fa-balance-scale-right",
                         color_box=(249, 139, 35),
                         i=len(df_latest[df_latest["L/R Imbalance"]==True]["Player ID"].unique())),
                unsafe_allow_html=True)
with no_rtp:
    st.markdown(info_box(sline="Strength Gain/Loss",
                         iconname = "fas fa-exclamation-circle",
                         color_box=(235, 83, 83),
                         i=len(df_latest[df_latest["RTP Level"]!=0]["Player ID"].unique())),
                unsafe_allow_html=True)
                
st.markdown("---")

# player test details
metrics = ["Max Force (N)","Max Torque (Nm)" , "Avg Force (N)", "Max Impulse (Ns)"]
with st.container():
    player, team = st.columns(2)
    with team:
        max_force, max_torque = st.columns(2)
        avg_force, max_impulse = st.columns(2)
        with max_force:
            st.altair_chart(draw_alt(df_player.dropna(), metrics[0]), 
                            use_container_width=True, theme="streamlit")
        with max_torque:
            st.altair_chart(draw_alt(df_player.dropna(), metrics[1]), 
                            use_container_width=True, theme="streamlit")
        with avg_force:
            st.altair_chart(draw_alt(df_player.dropna(), metrics[2]), 
                            use_container_width=True, theme="streamlit")
        with max_impulse:
            st.altair_chart(draw_alt(df_player.dropna(), metrics[3]), 
                            use_container_width=True, theme="streamlit")
        # st.subheader("Team Overview")
        # df_team = df1_filtered.sort_values(by="Datetime UTC")
        # c = alt.Chart(df_team.drop_duplicates(subset=["Player ID"])).mark_bar().encode(
        #     x="Age Group",
        #     y="count(Player ID)",
        #     color = "Position"
        # ).properties(height=300)
        # st.altair_chart(c, use_container_width=True, theme="streamlit")
        
    with player: 
        st.subheader(f"{option_test} Test Result - **Player {option_player}**  ")
        # add session to update selection 

        column_to_check = ['L Max Force (N)_comp', 'R Max Force (N)_comp', 'L Max Torque (Nm)_comp', 'R Max Torque (Nm)_comp', 'L Avg Force (N)_comp', 'R Avg Force (N)_comp',
       'L Max Impulse (Ns)_comp', 'R Max Impulse (Ns)_comp']
        
        bla_to_check = ['Max Force (N) Imbalance', 'Max Torque (Nm) Imbalance', 'Max Avg Force (N) Imbalance', 'Avg Force (N) Imbalance']
        
        not_pass = [x[:-5] for x in column_to_check if df_player[x].values[-1]]
        if len(not_pass)!=0:
            not_pass = ", ".join(str(x) for x in not_pass)
        else: 
            not_pass = ""
        not_balance = [x for x in bla_to_check if (df_player[x].abs().round(4).values[-1] >= IMBALANCE) ]
        not_balance = ", ".join(str(x) for x in not_balance)

        # description
        st.markdown(f"""In the lastest {option_test} test on {df_player["Datetime UTC"].max()},
                    Player {option_player}, the {df_player["Position"].values[-1]} of 
                    {df_player["Age Group"].values[-1]}:""")
        # check if all test passed
        if (df_player["RTP Level"].values[-1]==0):
            st.markdown("- Has passed NordBord tests.")
        else:
            st.markdown(f"""- <span style="color:#FF4B4B;">  {not_pass} </span> not passed.""", unsafe_allow_html=True)
        # check if imbalance
        if (df_player["L/R Imbalance"].values[-1]):
            st.markdown(f"""- The result of <span style="color:#FF4B4B;"> {not_balance}</span> is not balanced on both feet. """, unsafe_allow_html=True)
        else:
            st.markdown("- Both feet are balanced.")
        
        st.markdown("**Comment:**")
        comment_list = comment_table[(comment_table["Player ID"] == option_player) & 
                               (comment_table["Test"] ==  option_test)]["Comment"].values
        if len(comment_list)==0:
            st.markdown("Ask sports scientist for further advice.")
        else:
            for x in comment_list:
                st.markdown(f"- {x}")
    
        st.markdown('''
                    <style>
                    [data-testid="stMarkdownContainer"] ul{
                        padding-left:40px;
                    }
                    </style>
                    ''', unsafe_allow_html=True)

        plt.style.use("dark_background")
        # add comment
        comment = st.text_input('Add Comment:', '')
        if st.button('Submit'):
            submit_comment(option_player, option_test, comment, comment_table)
            # reset comments
            comment = ""
            st.experimental_rerun()

        




st.subheader(f"{option_test} Test Data - **Player {option_player}**  ")
st.dataframe(df_player[['Player ID', "Datetime UTC", 'Test', 'L Reps', 'R Reps', 'L Max Force (N)', 
                     'R Max Force (N)', 'L Max Torque (Nm)', 'R Max Torque (Nm)', 
                     'L Avg Force (N)', 'R Avg Force (N)', 'L Max Impulse (Ns)',
                       'R Max Impulse (Ns)', 'Code', 'Status', 'Age Group']].sort_values(["Datetime UTC"],ascending=[False]))
st.subheader(f"Player {option_player} Stats")
st.dataframe(df_player[['Player ID', 'Test', 'L Max Force (N)_mean', 'R Max Force (N)_mean',
       'L Max Torque (Nm)_mean', 'R Max Torque (Nm)_mean',
       'L Avg Force (N)_mean', 'R Avg Force (N)_mean',
       'L Max Impulse (Ns)_mean', 'R Max Impulse (Ns)_mean',
       'L Max Force (N)_std', 'R Max Force (N)_std', 'L Max Torque (Nm)_std',
       'R Max Torque (Nm)_std', 'L Avg Force (N)_std', 'R Avg Force (N)_std',
       'L Max Impulse (Ns)_std', 'R Max Impulse (Ns)_std']].drop_duplicates())

st.markdown("---")
st.subheader("Reference")
st.markdown("""
- [A Review of the NordBord Hamstring Testing System](https://simplifaster.com/articles/review-nordbord-hamstring-testing-system/)
 > We currently require the athlete to be at 90% of their pre-injury strength values before they are able to fully participate in practice.
- [ISO 60](https://support.vald.com/hc/en-au/articles/8825899887001-NordBord-Test-ISO-60-)
- The latest test value with more than +/-2 Z-Score will be classified as to be recovered.
- The asymmetry >= 10% between both feet will be identified as imbalance 
 
 """)

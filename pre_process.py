import pandas as pd
import numpy as np
from scipy.stats import zscore
import datetime
import time


import altair as alt
# process data
RTP_THRESHOLD = 0.9
IMBALANCE = 0.1


def task1_clean_data(rtp_theshold=RTP_THRESHOLD, imbalance=IMBALANCE):

    nb = pd.read_excel("./data/Southampton/Task 1 Data.xlsx",
                       sheet_name="Nordboard Data")
    players = pd.read_excel(
        "./data/Southampton/Task 1 Data.xlsx", sheet_name="Player Data")

    nb = nb.dropna(subset=["Player ID"])
    nb["Player ID"] = nb["Player ID"].astype(int)

    nb["Date UTC"] = nb["Date UTC"].astype(str)
    nb["Time UTC"] = nb["Time UTC"].astype(str)
    nb["Datetime UTC"] = nb["Date UTC"] + " " + nb["Time UTC"]
    nb["Datetime UTC"] = pd.to_datetime(nb["Datetime UTC"])

    id_columns = ['Player ID', "Datetime UTC", "Test"]
    players.columns = ['Player ID', 'Initial', 'Code', 'Code2', 'Number', 'Position', 'Status',
                       'Age Group']

    df = pd.merge(nb, players)

    df["Max Force (N) Imbalance"] = (df["L Max Force (N)"] -
                                     df["R Max Force (N)"]) / df["R Max Force (N)"]
    df["Max Torque (Nm) Imbalance"] = (df["L Max Torque (Nm)"] -
                                       df["R Max Torque (Nm)"]) / df["R Max Torque (Nm)"]
    df["Max Avg Force (N) Imbalance"] = (
        df["L Avg Force (N)"] - df["R Avg Force (N)"]) / df["R Avg Force (N)"]
    df["Avg Force (N) Imbalance"] = (df["L Avg Force (N)"] -
                                     df["R Avg Force (N)"]) / df["R Avg Force (N)"]

    df["Test"] = df["Test"].str.replace('Iso Prone', 'ISO Prone')

    # Step 2: Group the DataFrame by 'Player ID' and 'Test'
    grouped = df.sort_values(by="Datetime UTC").groupby(['Player ID', 'Test'])

    # Step 3: Apply the function to the columns of interest
    cols_of_interest = ['L Max Force (N)', 'R Max Force (N)', 'L Max Torque (Nm)', 'R Max Torque (Nm)',
                        'L Avg Force (N)', 'R Avg Force (N)', 'L Max Impulse (Ns)', 'R Max Impulse (Ns)']
    

    # NOTE: rolling average of 10 windows approach
    # to_roll = df.sort_values(by=["Player ID","Test","Datetime UTC"])
    # grouped = to_roll.groupby(["Player ID", "Test"])
    # results = grouped[cols_of_interest].transform(lambda x: x.rolling(10, 1).mean())
    # results["Player ID"] = to_roll["Player ID"]
    # results["Test"] = to_roll["Test"]
    # results["Datetime UTC"] = to_roll["Datetime UTC"]
    # # take the latest avg
    # results = results.sort_values("Datetime UTC").groupby(
    #     ['Player ID', 'Test']).tail(1).sort_index()

    # Z-score approach
    grouped = df.groupby(['Player ID', 'Test'])
    cols_of_interest = ['L Max Force (N)', 'R Max Force (N)', 'L Max Torque (Nm)', 'R Max Torque (Nm)', 'L Avg Force (N)', 'R Avg Force (N)', 'L Max Impulse (Ns)', 'R Max Impulse (Ns)']
    results_mean = grouped[cols_of_interest].mean().reset_index()
    results_std = grouped[cols_of_interest].agg(np.std).reset_index()
    results = pd.merge(results_mean, results_std, on =["Player ID", "Test"], suffixes=["_mean", "_std"])

    latest_test = df.sort_values("Datetime UTC").groupby(
        ['Player ID', 'Test']).tail(1).sort_index()

    # find imbalance >10%
    latest_test["L/R Imbalance"] = ((latest_test[['Max Force (N) Imbalance', 'Max Torque (Nm) Imbalance',
                                                  'Max Avg Force (N) Imbalance', 'Avg Force (N) Imbalance']].abs().round(4) > imbalance) | 
                                                  np.isclose(latest_test[['Max Force (N) Imbalance', 'Max Torque (Nm) Imbalance',                                                                                                  
                                                                          'Max Avg Force (N) Imbalance', 'Avg Force (N) Imbalance']], 0.1)).any(axis=1)
    # add suffix
    latest_test.columns = [str(col) + "_latest" if col not in ["Player ID", "Test"] else str(col) for col in latest_test.columns ]


    # merge max and latest to find difference
    is_RTP = pd.merge(latest_test, results, on=[
                      "Player ID", "Test"])
    
    is_RTP = is_RTP[['Player ID', 'Test', 'L Max Force (N)_latest', 'R Max Force (N)_latest',
                    'L Max Torque (Nm)_latest', 'R Max Torque (Nm)_latest',
                     'L Avg Force (N)_latest', 'R Avg Force (N)_latest',
                     'L Max Impulse (Ns)_latest', 'R Max Impulse (Ns)_latest',
                     'L Max Force (N)_mean', 'R Max Force (N)_mean', 
                     'L Max Torque (Nm)_mean', 'R Max Torque (Nm)_mean', 
                     'L Avg Force (N)_mean', 'R Avg Force (N)_mean', 
                     'L Max Impulse (Ns)_mean', 'R Max Impulse (Ns)_mean', 
                     'L Max Force (N)_std', 'R Max Force (N)_std', 
                     'L Max Torque (Nm)_std', 'R Max Torque (Nm)_std', 
                     'L Avg Force (N)_std', 'R Avg Force (N)_std', 
                     'L Max Impulse (Ns)_std','R Max Impulse (Ns)_std']]
    


    df_rtp = pd.merge(df, is_RTP, on=["Player ID", "Test"])

    

    # recalculate imbalance
    df_rtp["L/R Imbalance"] = ((df_rtp[['Max Force (N) Imbalance', 'Max Torque (Nm) Imbalance',
                                'Max Avg Force (N) Imbalance', 'Avg Force (N) Imbalance']].abs().round(4) > 0.1) | 
                                np.isclose(df_rtp[['Max Force (N) Imbalance', 'Max Torque (Nm) Imbalance',
                 'Max Avg Force (N) Imbalance', 'Avg Force (N) Imbalance']], 0.1)).any(axis=1)

    df_rtp["Position"] = df_rtp["Position"].str.strip()
    df_rtp["Status"] = df_rtp["Status"].str.strip()

    # calculate z_score
    to_compare = ["L Max Force (N)", "R Max Force (N)",
                  "L Max Torque (Nm)", "R Max Torque (Nm)",
                  "L Avg Force (N)", "R Avg Force (N)",
                  "L Max Impulse (Ns)", "R Max Impulse (Ns)"
                  ]

    # calculate z-score
    for col in to_compare:
        df_rtp[f"{col}_zscore"] = (df_rtp[f"{col}"] - df_rtp[f"{col}_mean"]) / df_rtp[f"{col}_std"]
        df_rtp[f"{col}_comp"] = abs(((df_rtp[f"{col}"] - df_rtp[f"{col}_mean"]) / df_rtp[f"{col}_std"])) >2

    # calculate pass metrics 
    df_rtp["RTP Level"] = df_rtp[[x + "_comp" for x in to_compare]].sum(axis=1)
    #df_rtp["RTP Pass"] = df_rtp[[x + "_comp" for x in to_compare]].all(axis=1)
    # df_rtp.to_csv("../data/Southampton/task1_output.csv", index=False)

    return df_rtp


def info_box(color_box=(255, 75, 75), iconname="fas fa-balance-scale-right", sline="Observations", i=123):
    wch_colour_box = color_box
    wch_colour_font = (0, 0, 0)
    fontsize = 28
    valign = "left"
    iconname = iconname
    sline = sline
    lnk = '<link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.12.1/css/all.css" crossorigin="anonymous">'
    i = i

    htmlstr = f"""<p style='background-color: rgb({wch_colour_box[0]}, 
                                                {wch_colour_box[1]}, 
                                                {wch_colour_box[2]}, 0.75); 
                            color: rgb({wch_colour_font[0]}, 
                                    {wch_colour_font[1]}, 
                                    {wch_colour_font[2]}, 0.75); 
                            font-size: {fontsize}px; 
                            border-radius: 7px; 
                            padding-left: 12px; 
                            padding-top: 18px; 
                            padding-bottom: 18px; 
                            line-height:25px;'>
                            <i class='{iconname} fa-xs'></i> {i}
                            </style><BR><span style='font-size: 18px; 
                            margin-top: 0;'>{sline}</style></span></p>"""

    return lnk + htmlstr


def melt_df(col, df):
    df_l = df[["Datetime UTC", f'L {col}', f'L {col}_mean']]
    df_l.columns = ["Datetime UTC", col, f'{col}_mean']
    df_l["Foot"] = "L"

    df_r = df[["Datetime UTC", f'R {col}', f'R {col}_mean']]
    df_r.columns = ["Datetime UTC", col, f'{col}_mean']
    df_r["Foot"] = "R"

    return pd.concat([df_l, df_r])


def draw_alt(source, col):
    source_m = melt_df(col, source)
    selection = alt.selection_multi(fields=['Foot'], bind='legend')
    interval = alt.selection_interval(encodings=['x'])


    avg_L = alt.Chart(source_m).mark_line(strokeDash=[1,3]).encode(
    alt.X("Datetime UTC"),
    alt.Y(f'{col}_mean'),
    alt.Color("Foot"),
    )
    
    chart = alt.Chart(source_m).mark_line(point=True).encode(
        alt.X("Datetime UTC"),
        alt.Y(col, axis=alt.Axis(title=f'{col}')),
        alt.Color("Foot"),
        alt.Tooltip([col, "Foot"]),
        opacity=alt.condition(selection, alt.value(1), alt.value(0.2))
        ).add_selection(selection
                        ).properties(width=300, height=300
                        ).interactive()
    
    return chart + avg_L


def cal_quantile(df_rtp, player_id):
    group = df_rtp[df_rtp["Player ID"] == player_id]["Age Group"].values[-1]
    test = df_rtp[df_rtp["Player ID"] == player_id]["Test"].values[-1]
    to_calc = df_rtp[(df_rtp["Age Group"] == group) & (df_rtp["Test"] == test)][['L Max Force (N)',
                                                                                 'R Max Force (N)', 'L Max Torque (Nm)', 'R Max Torque (Nm)',
                                                                                'L Avg Force (N)', 'R Avg Force (N)', 'L Max Impulse (Ns)', 'R Max Impulse (Ns)'
                                                                                 ]]

    median = to_calc.median().to_dict()
    q25 = to_calc.quantile(0.25).to_dict()
    q75 = to_calc.quantile(0.75).to_dict()
    return q25, median, q75

def load_comment():
    return pd.read_csv("./data/Southampton/task1_comment.csv")
def submit_comment(player_id, test, text, comment_table):
    ts = time.time()
    now = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    comment_table = comment_table.append({'Player ID': player_id, 'Test':test,
                              'Timestamp':now, 'Comment': text}, ignore_index=True)
    comment_table.to_csv("./data/Southampton/task1_comment.csv", encoding='utf-8', index=False)
    


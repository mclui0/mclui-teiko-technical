#!/usr/bin/env python
"""
Teiko Technical Test Dashboard File
"""

import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px  # for interactive plots
import math
from scipy.stats import mannwhitneyu

########################
### Helper Functions ###
########################

def fetch_data(query, db_path="cell-count.db"):
    """Helper function to fetch data from the database
    In: query (str), database path (str)
    Out: Pandas dataframe
    """
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

@st.cache_data  # cache data to improve performance
def distinct_values(column):
    """Helper function to retrieve distinct values for a column
    In: column (str)
    Out: list of distinct values (list)
    """
    query = f"SELECT DISTINCT {column} FROM cell_counts ORDER BY {column}"
    return fetch_data(query)[column].dropna().tolist()


def render_table(df, key, preview_rows=25):
    """Helper function to render a table, default 25 rows with option to show all
    In: Pandas dataframe, key (str), preview_rows (int)
    Out: N/A
    """
    show_all = st.checkbox(  # checkbox toggle setup
        "Show all rows",
        key=f"chk_{key}",
        value=False  # default state
    )
    if show_all:
        visible_df = df
    else:
        visible_df = df.head(preview_rows)  # default state
    st.caption(f"Currently showing {len(visible_df)} of {len(df)} results.")
    st.dataframe(visible_df)

############################################
### PART 2: Page Setup and Data Overview ###
############################################

# Set page title and desc, page setup
st.title("Immune Cell Population Dashboard")
# st.markdown("Use the filters below to analyze treatment statistics.")
st.subheader("Data Overview")

df_overview = fetch_data("SELECT * FROM cell_frequencies")
df_overview['percentage'] = df_overview['percentage'].apply(lambda x: f"{x:.2f}%")  # format 2sf
df_overview_disp = (df_overview.rename(columns={
    "sample": "Sample",
    "total_count": "Total Count",
    "population": "Population",
    "count": "Population Count",
    "percentage": "Relative Frequency"
}))
render_table(df_overview_disp, key="overview")
st.markdown("---")  # separator


#######################################################
### PART 3: Filtering Data and Statistical Analysis ###
#######################################################

########################################
### Dropdowns and Query Construction ###
########################################

st.subheader("Filter Data")

# Filter selections
projects = distinct_values("project")
conditions = distinct_values("condition")
sexes = distinct_values("sex")
treatments = distinct_values("treatment")
responses = distinct_values("response")
sample_types = distinct_values("sample_type")
times = distinct_values("time_from_treatment_start")

# Filter textboxes and dropdowns
col1, col2 = st.columns(2)
with col1:
    selected_project = st.selectbox("Project", ["All"] + projects)
    selected_condition = st.selectbox("Condition", ["All"] + conditions)
    selected_sex = st.selectbox("Sex", ["All"] + sexes)
    selected_treatment = st.selectbox("Treatment", ["All"] + treatments)
with col2:
    selected_response = st.multiselect("Response", responses, default=responses)
    selected_sample_type = st.selectbox("Sample type", ["All"] + sample_types)
    selected_time = st.selectbox("Time from treatment start", ["All"] + times)

    # Cell population filter
    populations = ["b_cell", "cd8_t_cell", "cd4_t_cell", "nk_cell", "monocyte"]
    selected_populations = st.multiselect("Cell populations", populations, default=populations)

# Build query based on selections
query = "SELECT * FROM cell_counts WHERE 1=1"
if selected_project != "All":
    query += f" AND project = '{selected_project}'"
if selected_condition != "All":
    query += f" AND condition = '{selected_condition}'"
if selected_sex != "All":
    query += f" AND sex = '{selected_sex}'"
if selected_sample_type != "All":
    query += f" AND sample_type = '{selected_sample_type}'"
if selected_time != "All":
    query += f" AND time_from_treatment_start = '{selected_time}'"
if selected_response:
    query += f" AND response IN ({','.join(f'\"{r}\"' for r in selected_response)})"
if selected_treatment != "All":
    query += f" AND treatment = '{selected_treatment}'"
df_filtered = fetch_data(query)

#########################
### Filter Data Table ###
#########################

# Calculate total counts for all populations early (prevent query from truncating calculations)
all_population_cols = ["b_cell", "cd8_t_cell", "cd4_t_cell", "nk_cell", "monocyte"]
df_filtered["total_count_all"] = df_filtered[all_population_cols].sum(axis=1)

# Prepare data for plotting - formatting
df_plot = pd.melt(
    df_filtered,
    id_vars=["project", "sample", "response", "condition", "sex", "treatment", "sample_type", "time_from_treatment_start"],
    value_vars=selected_populations,
    var_name="population",
    value_name="count"
)

# Calculate percentages
df_plot = df_plot.merge(
    df_filtered[["sample", "total_count_all"]].rename(columns={"total_count_all": "total_count"}),
    on="sample"
)
df_plot["percentage"] = (df_plot["count"] / df_plot["total_count"])

# Label and render table
df_plot_disp = (df_plot.rename(columns={
    "project": "Project",
    "sample": "Sample",
    "response": "Response",
    "condition": "Condition",
    "sex": "Sex",
    "treatment": "Treatment",
    "sample_type": "Sample Type",
    "time_from_treatment_start": "Time Elapsed",
    "population": "Population",
    "count": "Population Count",
    "total_count": "Total Count",
    "percentage": "Relative Frequency"
}))
df_plot_disp['Relative Frequency'] = df_plot_disp['Relative Frequency'].apply(lambda x: f"{x * 100:.2f}%")  # format 2sf
render_table(df_plot_disp, key="filtered")

#########################
### Quick Stats Table ###
#########################

# Show statistical stats for numerically significant columns
stats_cols = [["count","Population Count"], ["total_count","Total Count"], ["percentage","Relative Frequency"]]
stats_data = []
for col in stats_cols:
    desc = df_plot[col[0]].describe()
    stats_data.append({
        "Metric": col[1],
        "Mean": f"{desc['mean']:.2f}",
        "Std": f"{desc['std']:.2f}",
        "Min": f"{desc['min']:.2f}",
        "25%": f"{desc['25%']:.2f}",
        "50% (Median)": f"{desc['50%']:.2f}",
        "75%": f"{desc['75%']:.2f}",
        "Max": desc["max"]
    })
df_stats = pd.DataFrame(stats_data)
st.markdown("##### **Quick Stats of Filtered Data**")

# Display total results
st.caption(f"Total filtered results: {len(df_plot)}")
st.dataframe(df_stats, hide_index=True)  # no need for show/hide all
st.caption("*Note that \"Total Count\" is always calculated with respect to" \
" all cell populations regardless of filter selection.*")

###############################
### Cell Population Boxplot ###
###############################

# Render boxplot
st.subheader("Relative Frequency of Cell Populations by Response")
fig = px.box(
    df_plot,
    x="population",
    y="percentage",
    color="response",
    points="all",
    color_discrete_map={"yes":"green", "no":"red"}
)
fig.layout.yaxis.title = "Relative Frequency"
fig.layout.xaxis.title = "Cell Population"
fig.layout.legend.title = "Response"
st.plotly_chart(fig)

################################
### Summary Statistics Table ###
################################

# Display summary statistics
summary_raw = df_plot.groupby(["population", "response"])['percentage'].agg(['mean','median','std']).reset_index()
summary = summary_raw.pivot(index='population', columns='response', values=['mean','median','std'])
summary.columns = [f"{stat}_{resp}" for stat, resp in summary.columns]

# Add p-value and significance
summary['p_value'] = math.nan
summary['significant'] = "no"  # default no

# Run mannwhitneyu for each population
for pop in df_plot['population'].unique():
    group_responder = df_plot[(df_plot['population'] == pop) & (df_plot['response'] == 'yes')]['percentage']
    group_nonresponder = df_plot[(df_plot['population'] == pop) & (df_plot['response'] == 'no')]['percentage']

    # Only run test if both groups have data
    if len(group_responder) > 0 and len(group_nonresponder) > 0:
        stat, p_value = mannwhitneyu(group_responder, group_nonresponder, alternative='two-sided')
        summary.loc[pop, 'p_value'] = p_value
        if p_value < 0.05:
            summary.loc[pop, 'significant'] = "yes"

# Reorder and render
st.subheader("Statistics by Population")
pop_order = ["b_cell", "cd8_t_cell", "cd4_t_cell", "nk_cell", "monocyte"]
df_summary = summary.reindex(pop_order)  # reorder for consistency
df_summary_disp = (df_summary.reset_index().rename(columns={
    "population": "Population",
    "mean_no": "Mean (No)",
    "mean_yes": "Mean (Yes)",
    "median_no": "Median (No)",
    "median_yes": "Median (Yes)",
    "std_no": "Std (No)",
    "std_yes": "Std (Yes)",
    "p_value": "MWU p-value",
    "significant": "Significant (p < 0.05)"
}))
st.dataframe(df_summary_disp, hide_index=True)  # no need for show/hide all

import streamlit as st
import pandas as pd
import plotly.express as px

def render(df=None):
    st.header("Q7: What is the Average Operational Life Range of a Bearing Type in Specific Contexts?")

    col1, col2 = st.columns([1.3, 2])

    # --- Left Column: Definitions ---
    with col1:
        st.subheader("Goal and Definitions")
        st.markdown("""
        This question investigates **how long different bearing types typically last** within a clearly defined context:
        - **Industry**
        - **Asset class (machine type)**
        - **RPM**

        ### Method:
        - Grouped records by `(industry, machine_type, rpm_min)`
        - Within each group, aggregated **bearing type** statistics:
            - `avg_life`, `min_life`, `max_life`, and `sample count`
        - Only included bearing types with **≥ 10 samples** per context
        """)

        with st.expander("Code Snippet: Aggregating by Context"):
            st.code("""
grouped = df.groupby(["industry", "machine", "rpm", "bearing_type"]).agg(
    avg_life=("operational_days", "mean"),
    ...
)
""")

    # --- Right Column: Filter + Graphs ---
    with col2:
        st.subheader("Select Context to View Bearing Life Ranges")

        df_stats = pd.read_csv("exploration/outputs/q7/bearing_life_by_context.csv")
        df_stats[['industry', 'machine', 'rpm']] = df_stats['context_key'].str.split("|", expand=True)

        # Filters
        industries = sorted(df_stats["industry"].unique())
        selected_industry = st.selectbox("Select Industry", industries)

        machines = sorted(df_stats[df_stats['industry'] == selected_industry]["machine"].unique())
        selected_machine = st.selectbox("Select Machine Type", machines)

        rpms = sorted(df_stats[
            (df_stats['industry'] == selected_industry) &
            (df_stats['machine'] == selected_machine)
        ]["rpm"].unique())
        selected_rpm = st.selectbox("Select RPM", rpms)

        # Filter based on all 3
        filtered = df_stats[
            (df_stats['industry'] == selected_industry) &
            (df_stats['machine'] == selected_machine) &
            (df_stats['rpm'] == selected_rpm)
        ]

        if filtered.empty:
            st.warning("No bearing type found with ≥ 10 samples for this context.")
            return

        # Bar plot of average life
        fig = px.bar(
            filtered,
            x='bearing_type',
            y='avg_life',
            color='bearing_type',
            error_y=filtered['max_life'] - filtered['avg_life'],
            error_y_minus=filtered['avg_life'] - filtered['min_life'],
            labels={'avg_life': 'Average Operational Life (days)', 'bearing_type': 'Bearing Type'},
            title=f"Life Ranges of Bearing Types — {selected_industry}, {selected_machine}, {selected_rpm} RPM"
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("""
        - Bars show **average operational life**
        - Error bars show **min–max range** for each bearing type
        """)

        with st.expander("View Raw Data Table"):
            st.dataframe(filtered[[
                "bearing_type", "avg_life", "min_life", "max_life", "count"
            ]].rename(columns={
                "avg_life": "Avg Life (days)",
                "min_life": "Min",
                "max_life": "Max",
                "count": "Samples"
            }), hide_index=True)

    # --- Section: Machine + RPM Range Summary (Moved from Q6) ---
    st.divider()
    st.subheader("Average Operational Life by Machine Type and RPM Range")

    rpm_df = pd.read_csv("exploration/outputs/q6/machine_rpm_life_summary.csv")
    rpm_df['context'] = rpm_df['machine_type'] + " | " + rpm_df['rpm_range']
    rpm_df = rpm_df.sort_values(by="avg_life", ascending=False)

    machine_types = rpm_df['machine_type'].unique().tolist()
    selected_machine = st.selectbox("Filter by Machine Type", options=["All"] + machine_types)

    if selected_machine != "All":
        filtered_df = rpm_df[rpm_df['machine_type'] == selected_machine]
    else:
        filtered_df = rpm_df.copy()

    fig = px.bar(
        filtered_df,
        x="context",
        y="avg_life",
        color="avg_life",
        color_continuous_scale="YlGnBu",
        title="Avg Bearing Life by Machine Type & RPM Range",
        hover_data=["median_life", "count"],
        labels={"avg_life": "Avg Operational Life (days)", "context": "Machine | RPM Range"}
    )
    fig.update_layout(
        xaxis_title="Machine + RPM Range",
        yaxis_title="Avg Operational Life",
        xaxis_tickangle=-45,
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    - This helps identify **machine + RPM combinations** that tend to support **longer bearing life**.
    - Use this insight to guide operational settings or asset design decisions.
    """)

    with st.expander("📋 View Table"):
        st.dataframe(filtered_df, use_container_width=True)

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

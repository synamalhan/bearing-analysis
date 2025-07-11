import streamlit as st
import pandas as pd
import plotly.express as px

def render(df: pd.DataFrame):
    st.header("Exploratory Data Analysis (EDA)")

    col1, col2 = st.columns([1.3, 2])

    # --- Column 1: Information ---
    with col1:
        st.subheader("What We Set Out to Explore")

        st.markdown("""
        The goal of EDA is to understand the structure, distribution, and relationships in the bearing dataset.

        ### Key Questions Explored:
        - What’s the distribution of **bearing types**, **makes**, and **industries**?
        - How do **RPM values** vary across assets?
        - What is the typical **operational life** of bearings?
        - Are there patterns in **failure severity**?

        ### Assumptions:
        - `operational_days` is derived from: `timestamp_of_fault - subscription_start`
        - We ignore assets with missing date/time values
        - Missing severity values are treated as **non-failed (0)**

        """)

        with st.expander("Code: Operational Life Calculation"):
            st.code("""
df['subscription_start'] = pd.to_datetime(df['subscription_start'])
df['timestamp_of_fault'] = pd.to_datetime(df['timestamp_of_fault'])
df['operational_days'] = (df['timestamp_of_fault'] - df['subscription_start']).dt.days
df['severity'] = df['bearing_severity_class'].fillna(0).astype(int)
""", language='python')

        with st.expander("Code: RPM Range Normalization"):
            st.code("""
df['rpm_range'] = df['rpm_max'] - df['rpm_min']
""")

    # --- Column 2: Visual Output ---
    with col2:
        st.subheader("Bearing Severity Distribution")
        fig1 = px.histogram(df, x='severity', nbins=5, color_discrete_sequence=["#7b68ee"])
        fig1.update_layout(xaxis_title="Severity Class", yaxis_title="Count")
        st.plotly_chart(fig1, use_container_width=True)
        st.markdown("**Most bearings fall under severity 0 (non-failure), with a few critical failures (Class 3).**")

        st.divider()

        st.subheader("Operational Life Distribution")
        fig2 = px.histogram(df, x='operational_days', nbins=40, color_discrete_sequence=["#ffa07a"])
        fig2.update_layout(xaxis_title="Operational Days", yaxis_title="Frequency")
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown("**Most bearings last under 1000 days, with a long right tail indicating a few very long-lived bearings.**")

        st.divider()

        st.subheader("Top 10 Bearing Makes by Record Count")
        top_makes = df['bearing_make'].value_counts().nlargest(10).reset_index()
        top_makes.columns = ['Make', 'Count']
        fig3 = px.bar(top_makes, x='Make', y='Count', color='Make',
                      title='Top 10 Bearing Makes in Dataset',
                      color_discrete_sequence=px.colors.qualitative.Prism)
        st.plotly_chart(fig3, use_container_width=True)

        st.divider()

        st.subheader("RPM Range Distribution")
        df['rpm_range'] = df['rpm_max'] - df['rpm_min']
        fig4 = px.box(df, y='rpm_range', points='all', color_discrete_sequence=["#2e8b57"])
        fig4.update_layout(yaxis_title="RPM Range")
        st.plotly_chart(fig4, use_container_width=True)
        st.markdown("**Most assets have a fixed RPM, with occasional wide operational ranges.**")

        st.divider()

        st.subheader("View Sample of Dataset")
        st.dataframe(df.head(10))

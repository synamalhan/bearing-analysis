import streamlit as st
import pandas as pd
import plotly.express as px

def render(df=None):
    st.header("Q3: Does the Environment Impact Bearing Life?")

    col1, col2 = st.columns([1.3, 2])

    # --- Column 1: Context and Definitions ---
    with col1:
        st.subheader("Goal & Rationale")
        st.markdown("""
        We explore how **environmental conditions** affect bearing performance:
        - **Industry Type**
        - **Machine Type**
        - **Lubrication Method**

        ### Why This Matters:
        Understanding which contexts **reduce bearing lifespan** helps in:
        - Proactive maintenance strategies
        - Choosing the right bearing for the environment

        ### Statistical Insight:
        We use the **Kruskal-Wallis Test** to detect significant differences across groups:
        - **p < 0.05** → Group (e.g. industry) significantly affects bearing life

        ### Results:
        - `industry_type`: p = **0.00000**
        - `machine_type`: p = **0.00000**
        - `lubrication_method`: p = **0.00010**
        """)

        with st.expander(" What is the Kruskal-Wallis Test?"):
            st.markdown("""
            A non-parametric alternative to ANOVA.
            - Compares **medians** across 2+ groups
            - Does **not assume normal distribution**
            - Useful when comparing life spans across categories

            - **Null hypothesis**: All groups have the same median
            - **Low p-value**: At least one group differs
            """)

        with st.expander("Code Snippet"):
            st.code("""
groups = [g['operational_days'].values for _, g in df.groupby('industry_type') if len(g) >= 10]
stat, p = kruskal(*groups)
""", language="python")

    # --- Column 2: Visuals ---
    with col2:
        st.subheader(" Environmental Factors and Bearing Life")

        tab1, tab2, tab3 = st.tabs([" Industry Type", " Machine Type", " Lubrication Method"])

        # --- Load summaries ---
        industry_df = pd.read_csv("exploration/outputs/q3/industry_life_summary.csv")
        machine_df = pd.read_csv("exploration/outputs/q3/machine_life_summary.csv")
        lube_df = pd.read_csv("exploration/outputs/q3/lubrication_life_summary.csv")

        # --- Helper to draw bar plot + severity ---
        def render_environment_tab(df, group_col, label):
            df = df.sort_values(by='avg_life', ascending=False)

            bar = px.bar(
                df,
                x=group_col,
                y='avg_life',
                color='severity_rate',
                color_continuous_scale='OrRd',
                title=f"Average Bearing Life by {label}",
                labels={'avg_life': 'Avg Life (days)', 'severity_rate': 'Failure Rate'}
            )
            bar.update_layout(xaxis_title=label, yaxis_title="Average Life (days)")
            st.plotly_chart(bar, use_container_width=True)

            st.markdown(f" Lower bars with higher red indicate harsher environments for bearing performance.")

            with st.expander(" View Table"):
                st.dataframe(df)

        # --- Tab 1: Industry ---
        with tab1:
            render_environment_tab(industry_df, 'industry_type', 'Industry Type')

        # --- Tab 2: Machine Type ---
        with tab2:
            render_environment_tab(machine_df, 'machine_type', 'Machine Type')

        # --- Tab 3: Lubrication ---
        with tab3:
            render_environment_tab(lube_df, 'lubrication_method', 'Lubrication Method')

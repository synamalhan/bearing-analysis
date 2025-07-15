import streamlit as st
import pandas as pd
import plotly.express as px

def render(df=None):
    st.header("Q6: Does Make Impact Bearing Life Within the Same Industry + Asset + RPM?")

    col1, col2 = st.columns([1.3, 2])

    # --- Column 1: Explanatory Panel ---
    with col1:
        st.subheader("Goal and Conditions")
        st.markdown("""
        This question explores whether **bearing makes** differ significantly in operational life when:
        - Used in the **same industry**
        - On the **same asset type (machine type)**
        - Operating at the **same RPM range**

        If so, we **rank makes** by average lifespan within each context.

        ### Method:
        - Defined "context" = **industry + machine type + RPM**
        - Filtered for **contexts with ≥ 2 makes and ≥ 10 records per make**
        - Applied **Kruskal-Wallis test** to compare distributions
        """)

        with st.expander("What is Kruskal-Wallis Test?"):
            st.markdown("""
            A non-parametric test used to determine whether there are statistically significant differences
            between **two or more independent groups** of a continuous variable.
            - It does **not assume normality**
            - It's appropriate when comparing makes across varying distribution shapes
            """)

        with st.expander("Code: Compare Makes in Same Context"):
            st.code("""
for key, group in df.groupby("context_key"):
    if ≥2 valid makes with ≥10 samples:
        perform Kruskal-Wallis on operational_days
""")

    # --- Column 2: Visual & Filters ---
    with col2:
        st.subheader("Make Life Comparison in Each Context")

        # Load results
        df_all = pd.read_csv("exploration/outputs/q6/make_life_comparison_same_context.csv")
        df_sig = pd.read_csv("exploration/outputs/q6/significant_make_rankings.csv")

        # Context dropdown
        unique_contexts = df_all['context'].unique().tolist()
        selected_context = st.selectbox("Select Context (Industry | Machine | RPM)", unique_contexts)

        context_df = df_all[df_all['context'] == selected_context]
        is_significant = context_df['p_value'].iloc[0] < 0.05

        fig = px.bar(
            context_df,
            x='bearing_make',
            y='mean',
            color='bearing_make',
            text='count',
            title=f"Avg Life by Make in Context: {selected_context}",
            labels={'mean': 'Average Operational Life (days)', 'bearing_make': 'Make'}
        )
        fig.update_layout(showlegend=False, xaxis_title="Make", yaxis_title="Mean Life (days)")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown(f"""
        **Statistical Significance:** {'✅ Significant difference (p < 0.05)' if is_significant else '❌ No significant difference (p ≥ 0.05)'}  
        **Top Performer:** {context_df.iloc[0]['bearing_make']} with **{context_df.iloc[0]['mean']:.1f} days**
        """)

        with st.expander("View Context Table"):
            st.dataframe(context_df[['bearing_make', 'mean', 'count', 'p_value']], hide_index=True)

        st.divider()

        st.subheader("All Contexts with Significant Differences")

        sig_contexts = df_sig['context'].unique().tolist()
        st.markdown(f"Total: **{len(sig_contexts)}** contexts with significant make differences")

        with st.expander("Show Summary Table"):
            st.dataframe(
                df_sig[['context', 'bearing_make', 'mean', 'count', 'p_value']].sort_values(['context', 'mean'], ascending=[True, False]),
                use_container_width=True
            )
        
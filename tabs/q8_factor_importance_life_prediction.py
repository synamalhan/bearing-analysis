
import streamlit as st
import pandas as pd
import plotly.express as px

def render(df=None):
    st.header("Q8: Can Environmental and Operational Factors Predict Bearing Life?")

    col1, col2 = st.columns([1.3, 2])

    # --- Column 1: Methodology & Assumptions ---
    with col1:
        st.subheader("Goal & Approach")
        st.markdown("""
        This question evaluates if **environmental and operational features** can reliably predict **bearing lifespan**.

        ### Features considered:
        - **Industry Type**
        - **Asset Category (Machine Type)**
        - **Speed Type**
        - **Lubrication Method**
        - **Bearing Type**

        ### Model Used:
        - **Random Forest Regressor**
        - Non-linear, tree-based model that handles categorical variables well

        ### Assumptions:
        - All features were **label encoded** before training
        - **Operational life** = Days between subscription start and failure timestamp

        """)

        with st.expander("📄 Code: Model Training & Evaluation"):
            st.code("""
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)
r2_score(y_test, y_pred)
""", language="python")

        with st.expander("📘 What is Feature Importance?"):
            st.markdown("""
            Feature importance measures **how much each input variable** contributes to reducing prediction error in the model.
            Higher values = more impact on the output (bearing life).
            """)

    # --- Column 2: Output + Graphs ---
    with col2:
        st.subheader("Model Performance")

        # Load metrics
        try:
            with open("exploration/outputs/q8/model_metrics.txt", "r") as f:
                metrics = f.read()
            st.code(metrics)
        except FileNotFoundError:
            st.error("Model metrics file not found. Please run the notebook first.")

        st.subheader("Feature Importance")

        # Load and plot
        try:
            fi_df = pd.read_csv("exploration/outputs/q8/feature_importance.csv", index_col=0)
            fi_df = fi_df.sort_values(by='0')

            fig = px.bar(
                fi_df,
                x=fi_df['0'],
                y=fi_df.index,
                orientation='h',
                labels={'0': 'Importance Score'},
                title="Predictive Power of Environmental & Operational Factors"
            )
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("""
            - **Higher bars** = More predictive features
            - Typically, **bearing type** and **machine type** emerge as strongest predictors
            """)
        except FileNotFoundError:
            st.error("Feature importance file not found. Please ensure the model outputs are saved.")

        with st.expander("📋 View Raw Importance Table"):
            if 'fi_df' in locals():
                st.dataframe(fi_df.rename(columns={'0': 'Importance Score'}), use_container_width=True)

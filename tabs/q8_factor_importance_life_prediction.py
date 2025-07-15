import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image

def render(df=None):
    st.header("Q8: Can Environmental and Operational Factors Predict Bearing Life?")

    col1, col2 = st.columns([1.3, 2])

    with col1:
        st.subheader("Goal & Method")
        st.markdown("""
        This section evaluates if **operational + environmental features** can help predict **bearing lifespan**.

        ### Model Used:
        - **Random Forest Regressor**
        - Handles **nonlinear interactions** and **categorical inputs**

        ### Features Included:
        - Industry Type
        - Machine Type
        - Speed Type
        - Lubrication Method
        - Bearing Type

        ### Evaluation:
        - Train/Test Split
        - Multiple metrics (R², MAE, RMSE, MAPE)
        - Interpretability with:
            - Feature Importance
            - SHAP
            - Permutation Importance
        """)

        with st.expander("Code Snippet"):
            st.code("""
model = RandomForestRegressor()
model.fit(X_train, y_train)
preds = model.predict(X_test)
r2_score(y_test, preds)
""")

    with col2:
        st.subheader("Model Metrics")
        try:
            with open("exploration/outputs/q8/model_metrics.txt", "r") as f:
                metrics = f.read()
            st.code(metrics)
        except FileNotFoundError:
            st.error("Model metrics file not found.")

        st.subheader("Feature Importance")
        try:
            fi_df = pd.read_csv("exploration/outputs/q8/feature_importance.csv", index_col=0)
            fi_df = fi_df.sort_values(by='0')
            fig = px.bar(
                fi_df,
                x=fi_df['0'],
                y=fi_df.index,
                orientation='h',
                labels={'0': 'Importance Score'},
                title="Feature Importance (Gini)"
            )
            st.plotly_chart(fig, use_container_width=True)
        except:
            st.warning("Feature importance file missing.")

        with st.expander("View Raw Table"):
            if 'fi_df' in locals():
                st.dataframe(fi_df.rename(columns={'0': 'Importance Score'}), use_container_width=True)

        st.subheader("Actual vs Predicted")
        try:
            st.image("exploration/outputs/q8/actual_vs_predicted.png", use_column_width=True)
        except:
            st.warning("Actual vs Predicted image not found.")

        st.subheader("Residuals")
        try:
            st.image("exploration/outputs/q8/residual_hist.png", use_column_width=True)
        except:
            st.warning("Residual plot not found.")

        st.subheader("SHAP Summary")
        try:
            st.image("exploration/outputs/q8/shap_summary_dot.png", use_column_width=True, caption="SHAP Summary (Dot)")
            st.image("exploration/outputs/q8/shap_summary_bar.png", use_column_width=True, caption="SHAP Summary (Bar)")
        except:
            st.warning("SHAP plots missing.")

        st.subheader("Permutation Importance")
        try:
            perm_df = pd.read_csv("exploration/outputs/q8/permutation_importance.csv")
            fig_perm = px.bar(
                perm_df,
                x="Importance",
                y="Feature",
                orientation="h",
                title="Permutation Importance",
                labels={"Importance": "Impact on Prediction Error"}
            )
            st.plotly_chart(fig_perm, use_container_width=True)
        except:
            st.warning("Permutation importance file missing.")

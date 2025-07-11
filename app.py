import streamlit as st
from tabs import eda, q1_make_comparison, q2_bearing_vs_industry, q3_environment_vs_life, q4_lubrication_intervention, q5_failure_timing_analysis, q6_make_impact_same_context, q7_bearing_type_life_ranges, q8_factor_importance_life_prediction
st.set_page_config(page_title="Bearing Failure Analysis", layout="wide")
st.title("🔧 Bearing Failure Analysis Dashboard")

# Load data once and share across tabs
@st.cache_data
def load_data():
    import pandas as pd
    return pd.read_csv("cleaned_bearing_data.csv")

df = load_data()

# Define main content tabs
tab2, tab3, tab4 , tab5, tab6 , tab7, tab8, tab9= st.tabs(["Q1: EDA",  
                                               "Q2: Bearing vs Industry", "Q3: Environmental Factors", 
                                               "Q4: Lubrication Intervention", "Q5: Useful Life Analysis",
                                               "Q6: Make Life Comparison", "Q7: Bearing Type Life Ranges",
                                               "Q8: Factor Importance for Life Prediction"])


with tab2:
    eda.render(df)

# with tab2:
#     q1_make_comparison.render(df)

with tab3:
    q2_bearing_vs_industry.render(df)

with tab4:  
    q3_environment_vs_life.render(df)

with tab5:
    q4_lubrication_intervention.render(df)

with tab6:
    q5_failure_timing_analysis.render(df)

with tab7:
    q6_make_impact_same_context.render(df)

with tab8:
    q7_bearing_type_life_ranges.render(df)

with tab9:  
    q8_factor_importance_life_prediction.render(df)


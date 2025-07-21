import streamlit as st
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="Q14: Severity Prediction", layout="wide")
# Load data
@st.cache_data
def load_data():
    return pd.read_excel("data/Cleaned_Bearing_Dataset.xlsx")

df = load_data()

# Load your data

st.title("Q14. Can we predict bearing failure severity based on machine type and RPM range?")
st.markdown("Train a simple classifier to estimate severity level before failure occurs.")

# Create columns
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Filters")
    industry = st.selectbox("Select Industry", ["All"] + sorted(df["industry_type"].dropna().unique()))
    machine = st.selectbox("Select Machine Type", ["All"] + sorted(df["machine_type"].dropna().unique()))
    bearing = st.selectbox("Select Bearing Type", ["All"] + sorted(df["bearing_type_assigned_1"].dropna().unique()))

    if industry != "All":
        df = df[df["industry"] == industry]
    if machine != "All":
        df = df[df["machine_type"] == machine]
    if bearing != "All":
        df = df[df["bearing_type"] == bearing]

    # Drop rows with missing values for relevant columns
    df = df.dropna(subset=["bearing_severity_class", "machine_type", "rpm_min", "rpm_max"])

    if df.empty:
        st.warning("No data available for selected filters.")
        st.stop()

    # Feature engineering: average RPM
    df["rpm_avg"] = (df["rpm_min"] + df["rpm_max"]) / 2

    # Encode target and categorical features
    le_severity = LabelEncoder()
    df["severity_encoded"] = le_severity.fit_transform(df["bearing_severity_class"])

    X = df[["machine_type", "rpm_avg"]].copy()
    X["machine_type"] = LabelEncoder().fit_transform(X["machine_type"])
    y = df["severity_encoded"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestClassifier(random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

with col2:
    st.subheader("Model Evaluation")

    target_names = [str(cls) for cls in le_severity.classes_]
    report = classification_report(y_test, y_pred, target_names=target_names, output_dict=False)
    st.text(report)

    # Confusion matrix plot
    cm = confusion_matrix(y_test, y_pred)
    fig, ax = plt.subplots()
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", 
                xticklabels=target_names, yticklabels=target_names, ax=ax)
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    st.pyplot(fig)

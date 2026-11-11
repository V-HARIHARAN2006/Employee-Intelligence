
import streamlit as st
import pandas as pd
import joblib


st.title("🤖 Employee Attrition Prediction")
st.caption("Predict employee attrition using machine learning")

model = joblib.load("models/attrition_model.pkl")

df = pd.read_csv("dataset/employee_data.csv")

# Remove target and unnecessary columns
features = df.drop(
    columns=[
        "Attrition",
        "EmployeeCount",
        "EmployeeNumber",
        "Over18",
        "StandardHours"
    ],
    errors="ignore"
)

st.subheader("Enter Employee Information")

with st.form("prediction_form"):

    values = {}

    col1, col2 = st.columns(2)

    for i, column in enumerate(features.columns):

        with (col1 if i % 2 == 0 else col2):

            if pd.api.types.is_numeric_dtype(features[column]):

                values[column] = st.number_input(
                    column,
                    value=float(features[column].median())
                )

            else:

                options = features[column].dropna().unique().tolist()

                values[column] = st.selectbox(
                    column,
                    options
                )

    submitted = st.form_submit_button(
        "Predict Attrition",
        use_container_width=True
    )

if submitted:

    input_df = pd.DataFrame([values])

    prediction = model.predict(input_df)[0]
    probability = model.predict_proba(input_df)[0][1]

    st.divider()

    st.subheader("Prediction Result")

    col1, col2 = st.columns(2)

    if prediction == 1:
        col1.error("Higher Attrition Risk")
    else:
        col1.success("Lower Attrition Risk")

    col2.metric(
        "Predicted Attrition Probability",
        f"{probability * 100:.2f}%"
    )

    st.progress(float(probability))

    st.caption(
        "This is a model estimate, not a certainty. "
        "It should support human review rather than "
        "automatically determine employment decisions."
    )


import streamlit as st
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# =====================================================
# 1. PAGE CONFIGURATION
# =====================================================



BASE_DIR = Path(__file__).resolve().parent.parent

METRICS_PATH = BASE_DIR / "models" / "model_metrics.json"

# =====================================================
# 2. CUSTOM CSS
# =====================================================

st.markdown("""
<style>

.stApp {
    background-color: #F4F7FB;
}

[data-testid="stSidebar"] {
    background-color: #14243B;
}

[data-testid="stSidebar"] * {
    color: white;
}

.performance-title {
    font-size: 32px;
    font-weight: 800;
    color: #14243B;
}

.performance-subtitle {
    color: #718096;
    font-size: 15px;
    margin-bottom: 25px;
}

div[data-testid="stMetric"] {
    background-color: white;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #E2E8F0;
}

.section-title {
    font-size: 21px;
    font-weight: 750;
    color: #14243B;
    margin-top: 15px;
    margin-bottom: 15px;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# 3. LOAD MODEL METRICS
# =====================================================

st.markdown(
    '<div class="performance-title">'
    'Machine Learning Model Performance'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="performance-subtitle">'
    'Evaluate and compare machine learning algorithms '
    'used for employee attrition prediction.'
    '</div>',
    unsafe_allow_html=True
)

if not METRICS_PATH.exists():

    st.error(
        "Model evaluation results not found. "
        "Please execute python train_model.py first."
    )

    st.code("python train_model.py")

    st.stop()

try:

    with open(METRICS_PATH, "r") as file:
        data = json.load(file)

except Exception as error:

    st.error(f"Unable to load model metrics: {error}")
    st.stop()


# =====================================================
# 4. EXTRACT RESULTS
# =====================================================

best_model = data["best_model"]

comparison = pd.DataFrame(
    data["cross_validation_results"]
)

metrics = data["test_metrics"]

# =====================================================
# 5. BEST MODEL
# =====================================================

st.markdown(
    '<div class="section-title">Selected Machine Learning Model</div>',
    unsafe_allow_html=True
)

st.success(
    f"Best Performing Model: {best_model}"
)

# =====================================================
# 6. KPI METRICS
# =====================================================

st.markdown(
    '<div class="section-title">Final Test Performance</div>',
    unsafe_allow_html=True
)

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "Accuracy",
    f"{metrics['Accuracy'] * 100:.2f}%"
)

col2.metric(
    "Precision",
    f"{metrics['Precision'] * 100:.2f}%"
)

col3.metric(
    "Recall",
    f"{metrics['Recall'] * 100:.2f}%"
)

col4.metric(
    "F1 Score",
    f"{metrics['F1 Score'] * 100:.2f}%"
)

col5.metric(
    "ROC AUC",
    f"{metrics['ROC AUC']:.3f}"
)

st.caption(
    f"Evaluation performed on {metrics['Test Samples']} "
    "held-out test records."
)

st.divider()

# =====================================================
# 7. MODEL COMPARISON
# =====================================================

st.markdown(
    '<div class="section-title">Model Comparison</div>',
    unsafe_allow_html=True
)

st.write(
    "The following algorithms were compared using "
    "5-fold stratified cross-validation."
)

st.dataframe(
    comparison.style.format({
        "Accuracy": "{:.2%}",
        "Precision": "{:.2%}",
        "Recall": "{:.2%}",
        "F1 Score": "{:.2%}",
        "ROC AUC": "{:.3f}"
    }),
    use_container_width=True,
    hide_index=True
)

# =====================================================
# 8. VISUAL MODEL COMPARISON
# =====================================================

st.subheader("Algorithm Performance Comparison")

metric_options = [
    "Accuracy",
    "Precision",
    "Recall",
    "F1 Score",
    "ROC AUC"
]

selected_metric = st.selectbox(
    "Choose evaluation metric",
    metric_options,
    index=3
)

comparison_fig = px.bar(
    comparison,
    x="Model",
    y=selected_metric,
    color="Model",
    text=selected_metric,
    title=f"{selected_metric} Comparison",
    color_discrete_sequence=[
        "#2563EB",
        "#0EA5E9",
        "#6366F1",
        "#14B8A6"
    ]
)

comparison_fig.update_traces(
    texttemplate="%{text:.3f}",
    textposition="outside"
)

comparison_fig.update_layout(
    template="plotly_white",
    paper_bgcolor="white",
    plot_bgcolor="white",
    height=420,
    yaxis=dict(
        range=[0, 1.15],
        title=selected_metric
    ),
    xaxis_title="Machine Learning Algorithm"
)

st.plotly_chart(
    comparison_fig,
    use_container_width=True
)

st.divider()

# =====================================================
# 9. CONFUSION MATRIX
# =====================================================

st.markdown(
    '<div class="section-title">Confusion Matrix</div>',
    unsafe_allow_html=True
)

st.write(
    "The confusion matrix displays the correct and incorrect "
    "predictions made by the selected model."
)

cm = metrics["Confusion Matrix"]

matrix_df = pd.DataFrame(
    cm,
    index=["Actual Stayed", "Actual Left"],
    columns=["Predicted Stayed", "Predicted Left"]
)

col1, col2 = st.columns([1.2, 1])

with col1:

    confusion_fig = px.imshow(
        matrix_df,
        text_auto=True,
        color_continuous_scale="Blues",
        aspect="auto",
        title="Attrition Prediction Confusion Matrix"
    )

    confusion_fig.update_layout(
        template="plotly_white",
        paper_bgcolor="white",
        plot_bgcolor="white",
        height=400
    )

    st.plotly_chart(
        confusion_fig,
        use_container_width=True
    )

with col2:

    tn, fp, fn, tp = cm[0][0], cm[0][1], cm[1][0], cm[1][1]

    st.metric("True Negatives", tn)
    st.metric("False Positives", fp)
    st.metric("False Negatives", fn)
    st.metric("True Positives", tp)

    st.info(
        "False negatives represent employees who actually left "
        "but were incorrectly predicted to stay. This is an "
        "important error to monitor in attrition prediction."
    )

st.divider()

# =====================================================
# 10. ROC CURVE
# =====================================================

st.markdown(
    '<div class="section-title">ROC Curve Analysis</div>',
    unsafe_allow_html=True
)

roc_data = metrics["ROC Curve"]

fpr = roc_data["FPR"]
tpr = roc_data["TPR"]

roc_fig = go.Figure()

roc_fig.add_trace(
    go.Scatter(
        x=fpr,
        y=tpr,
        mode="lines",
        name=f"{best_model} (AUC = {metrics['ROC AUC']:.3f})",
        line=dict(
            color="#2563EB",
            width=3
        )
    )
)

roc_fig.add_trace(
    go.Scatter(
        x=[0, 1],
        y=[0, 1],
        mode="lines",
        name="Random Classifier",
        line=dict(
            color="#EF4444",
            dash="dash"
        )
    )
)

roc_fig.update_layout(
    title="Receiver Operating Characteristic Curve",
    xaxis_title="False Positive Rate",
    yaxis_title="True Positive Rate",
    template="plotly_white",
    paper_bgcolor="white",
    plot_bgcolor="white",
    height=450,
    xaxis=dict(range=[0, 1]),
    yaxis=dict(range=[0, 1])
)

st.plotly_chart(
    roc_fig,
    use_container_width=True
)

st.divider()

# =====================================================
# 11. CLASSIFICATION REPORT
# =====================================================

st.markdown(
    '<div class="section-title">Classification Report</div>',
    unsafe_allow_html=True
)

report = metrics["Classification Report"]

report_df = pd.DataFrame({
    "Class": ["Stayed", "Left"],
    "Precision": [
        report["Stayed"]["precision"],
        report["Left"]["precision"]
    ],
    "Recall": [
        report["Stayed"]["recall"],
        report["Left"]["recall"]
    ],
    "F1 Score": [
        report["Stayed"]["f1-score"],
        report["Left"]["f1-score"]
    ],
    "Support": [
        report["Stayed"]["support"],
        report["Left"]["support"]
    ]
})

st.dataframe(
    report_df.style.format({
        "Precision": "{:.3f}",
        "Recall": "{:.3f}",
        "F1 Score": "{:.3f}"
    }),
    use_container_width=True,
    hide_index=True
)

# =====================================================
# 12. DOWNLOAD RESULTS
# =====================================================

st.divider()

st.subheader("Export Model Evaluation")

csv = comparison.to_csv(index=False).encode("utf-8")

st.download_button(
    "Download Model Comparison CSV",
    data=csv,
    file_name="model_comparison.csv",
    mime="text/csv"
)

# =====================================================
# 13. FOOTER
# =====================================================

st.divider()

st.markdown(
    """
    <div style="text-align:center;color:#718096;
    font-size:12px;padding:20px;">

    EMPLOYEE INTELLIGENCE<br><br>

    Machine Learning Model Evaluation<br>

    Employee Attrition Prediction & Workforce Analytics

    </div>
    """,
    unsafe_allow_html=True
)

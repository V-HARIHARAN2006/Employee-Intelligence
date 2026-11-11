
from pathlib import Path
import json
import joblib
import pandas as pd

from sklearn.model_selection import (
    train_test_split,
    StratifiedKFold,
    cross_validate
)

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier
)

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    roc_curve,
    classification_report
)

# =====================================================
# 1. PROJECT PATHS
# =====================================================

BASE_DIR = Path(__file__).resolve().parent

DATA_PATH = BASE_DIR / "dataset" / "employee_data.csv"
MODEL_DIR = BASE_DIR / "models"

MODEL_DIR.mkdir(exist_ok=True)

# =====================================================
# 2. LOAD DATASET
# =====================================================

print("Loading employee dataset...")

df = pd.read_csv(DATA_PATH)

df.columns = df.columns.str.strip()

df["Attrition"] = (
    df["Attrition"]
    .astype(str)
    .str.strip()
    .str.capitalize()
)

df = df[df["Attrition"].isin(["Yes", "No"])].copy()

# Remove identifiers and constant columns
drop_columns = [
    "Attrition",
    "EmployeeNumber",
    "EmployeeCount",
    "Over18",
    "StandardHours"
]

X = df.drop(columns=drop_columns, errors="ignore")
y = df["Attrition"].map({"No": 0, "Yes": 1})

# =====================================================
# 3. IDENTIFY FEATURE TYPES
# =====================================================

numeric_features = X.select_dtypes(
    include=["number"]
).columns.tolist()

categorical_features = X.select_dtypes(
    exclude=["number"]
).columns.tolist()

# =====================================================
# 4. PREPROCESSING
# =====================================================

numeric_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler())
])

categorical_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("encoder", OneHotEncoder(handle_unknown="ignore"))
])

preprocessor = ColumnTransformer([
    ("num", numeric_pipeline, numeric_features),
    ("cat", categorical_pipeline, categorical_features)
])

# =====================================================
# 5. MACHINE LEARNING MODELS
# =====================================================

algorithms = {

    "Logistic Regression": LogisticRegression(
        max_iter=2000,
        class_weight="balanced",
        random_state=42
    ),

    "Decision Tree": DecisionTreeClassifier(
        max_depth=6,
        class_weight="balanced",
        random_state=42
    ),

    "Random Forest": RandomForestClassifier(
        n_estimators=200,
        class_weight="balanced",
        random_state=42
    ),

    "Gradient Boosting": GradientBoostingClassifier(
        random_state=42
    )
}

# =====================================================
# 6. TRAIN AND TEST SPLIT
# =====================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    stratify=y,
    random_state=42
)

# =====================================================
# 7. CROSS VALIDATION
# =====================================================

cv = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)

results = []

best_score = -1
best_name = None
best_pipeline = None

print("\nStarting model comparison...\n")

for name, algorithm in algorithms.items():

    pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", algorithm)
    ])

    scores = cross_validate(
        pipeline,
        X_train,
        y_train,
        cv=cv,
        scoring={
            "accuracy": "accuracy",
            "precision": "precision",
            "recall": "recall",
            "f1": "f1",
            "roc_auc": "roc_auc"
        }
    )

    avg_accuracy = scores["test_accuracy"].mean()
    avg_precision = scores["test_precision"].mean()
    avg_recall = scores["test_recall"].mean()
    avg_f1 = scores["test_f1"].mean()
    avg_auc = scores["test_roc_auc"].mean()

    results.append({

        "Model": name,

        "Accuracy": round(float(avg_accuracy), 4),

        "Precision": round(float(avg_precision), 4),

        "Recall": round(float(avg_recall), 4),

        "F1 Score": round(float(avg_f1), 4),

        "ROC AUC": round(float(avg_auc), 4)

    })

    print(f"Model: {name}")
    print(f"Accuracy: {avg_accuracy:.4f}")
    print(f"Precision: {avg_precision:.4f}")
    print(f"Recall: {avg_recall:.4f}")
    print(f"F1 Score: {avg_f1:.4f}")
    print(f"ROC AUC: {avg_auc:.4f}")
    print("-" * 40)

    if avg_f1 > best_score:

        best_score = avg_f1
        best_name = name
        best_pipeline = pipeline

# =====================================================
# 8. FINAL MODEL TRAINING
# =====================================================

print("\nTraining the selected model:", best_name)

best_pipeline.fit(X_train, y_train)

# =====================================================
# 9. TEST SET PREDICTION
# =====================================================

predictions = best_pipeline.predict(X_test)

probabilities = best_pipeline.predict_proba(X_test)[:, 1]

# =====================================================
# 10. EVALUATION METRICS
# =====================================================

accuracy = accuracy_score(y_test, predictions)

precision = precision_score(
    y_test, predictions, zero_division=0
)

recall = recall_score(
    y_test, predictions, zero_division=0
)

f1 = f1_score(
    y_test, predictions, zero_division=0
)

auc = roc_auc_score(
    y_test, probabilities
)

cm = confusion_matrix(
    y_test,
    predictions,
    labels=[0, 1]
)

fpr, tpr, thresholds = roc_curve(
    y_test,
    probabilities
)

test_metrics = {

    "Accuracy": float(accuracy),

    "Precision": float(precision),

    "Recall": float(recall),

    "F1 Score": float(f1),

    "ROC AUC": float(auc),

    "Confusion Matrix": cm.tolist(),

    "ROC Curve": {
        "FPR": fpr.tolist(),
        "TPR": tpr.tolist()
    },

    "Test Samples": int(len(y_test)),

    "Classification Report": classification_report(
        y_test,
        predictions,
        target_names=["Stayed", "Left"],
        output_dict=True,
        zero_division=0
    )

}

# =====================================================
# 11. SAVE TRAINED MODEL
# =====================================================

joblib.dump(
    best_pipeline,
    MODEL_DIR / "attrition_model.pkl"
)

# =====================================================
# 12. SAVE EVALUATION RESULTS
# =====================================================

output = {

    "best_model": best_name,

    "cross_validation_results": results,

    "test_metrics": test_metrics,

    "features": X.columns.tolist()

}

with open(
    MODEL_DIR / "model_metrics.json",
    "w"
) as file:

    json.dump(
        output,
        file,
        indent=4
    )

# =====================================================
# 13. DISPLAY FINAL RESULTS
# =====================================================

print("\n" + "=" * 50)

print("MODEL TRAINING COMPLETED")

print("=" * 50)

print("Best Model:", best_name)

print("\nFinal Test Metrics:")

print(f"Accuracy:  {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall:    {recall:.4f}")
print(f"F1 Score:  {f1:.4f}")
print(f"ROC AUC:   {auc:.4f}")

print("\nConfusion Matrix:")
print(cm)

print("\nModel saved successfully!")

print("Location:", MODEL_DIR)

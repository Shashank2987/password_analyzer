import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import LinearSVC
from sklearn.metrics import classification_report, accuracy_score

# Load dataset
df = pd.read_csv("trainer_dataset.csv")

# Clean
df.columns = df.columns.str.strip()
df.dropna(inplace=True)
df.drop_duplicates(inplace=True)

# Features and labels
X = df["password"].astype(str)
y = df["Strength"].astype(str)

# Encode labels
encoder = LabelEncoder()
y = encoder.fit_transform(y)

# Train/Test split
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# Pipeline
model = Pipeline([
    (
        "tfidf",
        TfidfVectorizer(
            analyzer="char",
            ngram_range=(2, 5)
        )
    ),
    (
        "classifier",
        LinearSVC(class_weight="balanced")
    )
])

# Train
model.fit(X_train, y_train)

# Evaluate
pred = model.predict(X_test)

print("Accuracy:", accuracy_score(y_test, pred))
print(classification_report(pred, y_test, target_names=encoder.classes_))

# Save
joblib.dump(model, "password_strength_model.pkl")
joblib.dump(encoder, "label_encoder.pkl")

print("Model saved successfully!")
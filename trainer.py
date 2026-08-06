import pandas as pd
import joblib

from sklearn.model_selection import train_test_split #Splits the data( training & testing in 80/20)
from sklearn.pipeline import Pipeline #makes it easy to convert text to TF - IDF, then train, test and predict 
from sklearn.feature_extraction.text import TfidfVectorizer #
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import LinearSVC
from sklearn.metrics import accuracy_score, classification_report

# Load dataset
df = pd.read_csv("trainer_dataset.csv")

# Clean
df.columns = df.columns.str.strip()
df.dropna(inplace=True)
df.drop_duplicates(inplace=True)

# Features and Labels
X = df["password"].astype(str)
y = df["Strength"].astype(str)

# Encode labels
encoder = LabelEncoder()
y_encoded = encoder.fit_transform(y)

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y_encoded,
    test_size=0.2,
    random_state=42,
    stratify=y_encoded
)

# Model pipeline
model = Pipeline([
    ("tfidf", TfidfVectorizer(
        analyzer="char",
        ngram_range=(2, 5)
    )),
    ("classifier", LinearSVC(class_weight="balanced"))
])

# Train
model.fit(X_train, y_train)

# Evaluate
pred = model.predict(X_test)

print("Accuracy:", accuracy_score(y_test, pred))
print(classification_report(y_test, pred, target_names=encoder.classes_))

# Save
joblib.dump(model, "password_strength_model.pkl")
joblib.dump(encoder, "label_encoder.pkl")

print("\n Files created:")
print("password_strength_model.pkl")
print("label_encoder.pkl")
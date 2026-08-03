import pandas as pd
import string
import math
import joblib

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report


# -----------------------------
# Load Dataset
# -----------------------------
df = pd.read_csv("dataset.csv", sep="\t")

df.dropna(inplace=True)
df.drop_duplicates(inplace=True)


# -----------------------------
# Feature Extraction
# -----------------------------
def entropy(password):
    if len(password) == 0:
        return 0

    charset = 0

    if any(c.islower() for c in password):
        charset += 26

    if any(c.isupper() for c in password):
        charset += 26

    if any(c.isdigit() for c in password):
        charset += 10

    if any(c in string.punctuation for c in password):
        charset += len(string.punctuation)

    if charset == 0:
        return 0

    return len(password) * math.log2(charset)


def sequential(password):
    sequences = [
        "abcdefghijklmnopqrstuvwxyz",
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        "0123456789",
        "qwertyuiop",
        "asdfghjkl",
        "zxcvbnm"
    ]

    p = password.lower()

    for seq in sequences:
        for i in range(len(seq)-2):
            if seq[i:i+3] in p:
                return 1

    return 0


def repeated(password):
    return int(any(password.count(c) >= len(password)//2 for c in set(password)))


def features(password):

    return {
        "length": len(password),

        "uppercase": sum(c.isupper() for c in password),

        "lowercase": sum(c.islower() for c in password),

        "digits": sum(c.isdigit() for c in password),

        "symbols": sum(c in string.punctuation for c in password),

        "has_upper": int(any(c.isupper() for c in password)),

        "has_lower": int(any(c.islower() for c in password)),

        "has_digit": int(any(c.isdigit() for c in password)),

        "has_symbol": int(any(c in string.punctuation for c in password)),

        "entropy": entropy(password),

        "sequential": sequential(password),

        "repeated": repeated(password)
    }


# -----------------------------
# Create Feature Matrix
# -----------------------------
X = pd.DataFrame(df["password"].apply(features).tolist())


# -----------------------------
# Encode Labels
# -----------------------------
encoder = LabelEncoder()

y = encoder.fit_transform(df["vuln"])


# -----------------------------
# Split Dataset
# -----------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


# -----------------------------
# Train Model
# -----------------------------
model = RandomForestClassifier(
    n_estimators=300,
    random_state=42
)

model.fit(X_train, y_train)


# -----------------------------
# Evaluate
# -----------------------------
pred = model.predict(X_test)

print("Accuracy:", accuracy_score(y_test, pred))

print("\nClassification Report\n")
print(classification_report(y_test, pred,
      target_names=encoder.classes_))


# -----------------------------
# Save Model
# -----------------------------
joblib.dump(model, "password_vulnerability_model.pkl")
joblib.dump(encoder, "label_encoder.pkl")

print("\nModel Saved Successfully!")
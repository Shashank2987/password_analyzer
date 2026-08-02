import math
import random
import string
import joblib
import numpy as np
import pymysql
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split

# ---------------------------------------------------------
# 1. Database Connection & Fetching Data
# ---------------------------------------------------------
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "your_mysql_password",
    "database": "your_database_name",
}


def fetch_weak_passwords():
    """Fetch all known weak passwords from your MySQL database."""
    connection = pymysql.connect(**DB_CONFIG)
    cursor = connection.cursor()
    cursor.execute("SELECT password FROM data")
    rows = cursor.fetchall()
    cursor.close()
    connection.close()

    # Clean list of weak passwords
    return [row[0] for row in rows if row[0]]


# ---------------------------------------------------------
# 2. Synthetic Dataset Generation
# ---------------------------------------------------------
def generate_strong_passwords(count=500):
    """Generate high-entropy synthetic strong passwords to balance training data."""
    strong_list = []
    chars = string.ascii_letters + string.digits + "!@#$%^&*()_+-="

    for _ in range(count):
        # Generate random length between 14 and 24
        length = random.randint(14, 24)
        pwd = "".join(random.choice(chars) for _ in range(length))
        strong_list.append(pwd)

    return strong_list


# ---------------------------------------------------------
# 3. Feature Extraction Engineering
# ---------------------------------------------------------
def calculate_entropy(s):
    """Calculates Shannon entropy of a string (randomness measure)."""
    if not s:
        return 0
    prob = [float(s.count(c)) / len(s) for c in dict.fromkeys(list(s))]
    return -sum([p * math.log(p, 2) for p in prob])


def extract_features(password):
    """Converts a password string into a numeric feature vector."""
    length = len(password)
    uppercase_cnt = sum(1 for c in password if c.isupper())
    lowercase_cnt = sum(1 for c in password if c.islower())
    digits_cnt = sum(1 for c in password if c.isdigit())
    special_cnt = sum(
        1 for c in password if not c.isalnum()
    )  # Symbols / Spaces
    entropy = calculate_entropy(password)

    # Feature vector array
    return [
        length,
        uppercase_cnt,
        lowercase_cnt,
        digits_cnt,
        special_cnt,
        entropy,
    ]


# ---------------------------------------------------------
# 4. Model Training Pipeline
# ---------------------------------------------------------
def train_model():
    print("Fetching weak passwords from MySQL database...")
    weak_passwords = fetch_weak_passwords()
    print(f"Loaded {len(weak_passwords)} weak passwords from DB.")

    # Generate an equal number of strong passwords to ensure class balance
    print("Generating synthetic strong passwords for training...")
    strong_passwords = generate_strong_passwords(count=len(weak_passwords))

    # Build dataset (X = Features, y = Target Labels)
    # Label 0 = Weak / Vulnerable, Label 1 = Strong
    X = []
    y = []

    for pwd in weak_passwords:
        X.append(extract_features(pwd))
        y.append(0)

    for pwd in strong_passwords:
        X.append(extract_features(pwd))
        y.append(1)

    X = np.array(X)
    y = np.array(y)

    # Split dataset: 80% Training, 20% Testing
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print("\nTraining Random Forest Classifier model...")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Evaluate Model
    y_pred = model.predict(X_test)
    print("\n--- Model Performance Evaluation ---")
    print(
        classification_report(
            y_test, y_pred, target_names=["Weak (0)", "Strong (1)"]
        )
    )

    # Save model to disk
    joblib.dump(model, "password_ml_model.pkl")
    print("Saved trained model to 'password_ml_model.pkl'.")

    return model


# ---------------------------------------------------------
# 5. Inference / Prediction Routine
# ---------------------------------------------------------
def predict_password_strength(model, password):
    features = np.array([extract_features(password)])

    # Predict class (0 or 1) and confidence probability
    prediction = model.predict(features)[0]
    probabilities = model.predict_proba(features)[0]

    confidence = (
        probabilities[1] if prediction == 1 else probabilities[0]
    ) * 100

    rating = "STRONG" if prediction == 1 else "WEAK / VULNERABLE"

    print("\n" + "=" * 45)
    print(f"ML PREDICTION FOR: '{password}'")
    print("=" * 45)
    print(f"Classification : {rating}")
    print(f"ML Confidence  : {confidence:.2f}%")
    print("=" * 45)


# ---------------------------------------------------------
# Main Execution Flow
# ---------------------------------------------------------
if __name__ == "__main__":
    trained_model = train_model()

    # Test with sample passwords
    test_inputs = ["password123", "P4ssw0rd!", "xK9#mQ2$vL8@zP1!"]

    for pwd in test_inputs:
        predict_password_strength(trained_model, pwd)
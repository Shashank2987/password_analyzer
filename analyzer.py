import math
import joblib
import numpy as np

# Feature Names evaluated by the ML Model
FEATURE_NAMES = [
    "Length",
    "Uppercase Count",
    "Lowercase Count",
    "Digits Count",
    "Special Chars Count",
    "Entropy (Bits)",
]


def calculate_entropy(s):
    """Calculates Shannon entropy of a string."""
    if not s:
        return 0
    prob = [float(s.count(c)) / len(s) for c in dict.fromkeys(list(s))]
    return -sum([p * math.log(p, 2) for p in prob])


def extract_features(password):
    """Generates the exact numerical feature vector fed into the ML model."""
    length = len(password)
    uppercase_cnt = sum(1 for c in password if c.isupper())
    lowercase_cnt = sum(1 for c in password if c.islower())
    digits_cnt = sum(1 for c in password if c.isdigit())
    special_cnt = sum(1 for c in password if not c.isalnum())
    entropy = calculate_entropy(password)

    return [
        length,
        uppercase_cnt,
        lowercase_cnt,
        digits_cnt,
        special_cnt,
        entropy,
    ]


def get_ml_feature_vulnerabilities(features):
    """Explains weaknesses directly from the ML feature values."""
    length, upper, lower, digits, special, entropy = features
    vulnerabilities = []

    # Check which features in the vector drag down the ML prediction score
    if length < 8:
        vulnerabilities.append(
            f"ML Feature 'Length' is critically low ({length}). Minimum recommended is 12."
        )
    elif length < 12:
        vulnerabilities.append(
            f"ML Feature 'Length' is sub-optimal ({length})."
        )

    if upper == 0:
        vulnerabilities.append(
            "ML Feature 'Uppercase Count' is 0 (Missing uppercase characters)."
        )

    if lower == 0:
        vulnerabilities.append(
            "ML Feature 'Lowercase Count' is 0 (Missing lowercase characters)."
        )

    if digits == 0:
        vulnerabilities.append(
            "ML Feature 'Digits Count' is 0 (Missing numbers)."
        )

    if special == 0:
        vulnerabilities.append(
            "ML Feature 'Special Chars Count' is 0 (Missing special symbols)."
        )

    if entropy < 3.0:
        vulnerabilities.append(
            f"ML Feature 'Entropy' is low ({entropy:.2f}). Character patterns are highly repetitive."
        )

    return vulnerabilities


def main():
    # Load trained ML model from disk
    try:
        with open("model.pkl", "rb") as f:
            ml_model = joblib.load("model.pkl")
        print("✅ Trained ML model ('model.pkl') loaded successfully.")
    except FileNotFoundError:
        print(
            "❌ Error: 'model.pkl' not found. Please train and save the model first."
        )
        return

    print("\n" + "=" * 55)
    print("        PURE MACHINE LEARNING PASSWORD ANALYZER")
    print("=" * 55)

    while True:
        user_pwd = input("\nEnter password to evaluate (or 'exit' to quit): ")
        if user_pwd.lower() == "exit":
            break

        if not user_pwd.strip():
            print("Please enter a valid password.")
            continue

        # 1. Extract raw numerical features for the ML model
        raw_features = extract_features(user_pwd)
        features_array = np.array([raw_features])

        # 2. Get ML Model Prediction & Confidence
        pred = ml_model.predict(features_array)[0]  # 0 = Weak, 1 = Strong
        probs = ml_model.predict_proba(features_array)[0]

        classification = "STRONG" if pred == 1 else "WEAK / VULNERABLE"
        confidence = (probs[1] if pred == 1 else probs[0]) * 100

        # 3. Print Output Report
        print("\n" + "-" * 50)
        print(f"ML MODEL EVALUATION FOR: '{user_pwd}'")
        print("-" * 50)
        print(f"ML Classification : {classification}")
        print(f"Model Confidence  : {confidence:.2f}%\n")

        # Display exact numerical inputs evaluated by the ML model
        print("📊 ML Model Input Features:")
        for name, val in zip(FEATURE_NAMES, raw_features):
            val_str = f"{val:.2f}" if isinstance(val, float) else str(val)
            print(f"  • {name:<20}: {val_str}")

        # Display feature-level weaknesses
        weaknesses = get_ml_feature_vulnerabilities(raw_features)
        if weaknesses:
            print(f"\n⚠️ Feature Weaknesses Detected ({len(weaknesses)}):")
            for w in weaknesses:
                print(f"  ❌ {w}")
        else:
            print("\n✅ All feature values meet ideal thresholds for the ML model.")

        print("-" * 50)


if __name__ == "__main__":
    main()
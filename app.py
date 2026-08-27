import math
import string
import os

from flask import Flask, request, jsonify, render_template

app = Flask(__name__)


# ============================================================
# LOAD TRAINED ML MODEL (falls back to a heuristic if absent)
# ============================================================

MODEL_PATH = "password_strength_model.pkl"
ENCODER_PATH = "label_encoder.pkl"

model = None
encoder = None
USING_ML_MODEL = False

if os.path.exists(MODEL_PATH) and os.path.exists(ENCODER_PATH):
    try:
        import joblib
        model = joblib.load(MODEL_PATH)
        encoder = joblib.load(ENCODER_PATH)
        USING_ML_MODEL = True
        print("✅ ML model loaded successfully.")
    except Exception as e:
        print(f"⚠️  Found model files but couldn't load them ({e}). Using heuristic fallback.")
else:
    print("⚠️  Model files not found (password_strength_model.pkl / label_encoder.pkl).")
    print("    Running with a transparent heuristic classifier instead.")
    print("    Drop the two .pkl files into this folder and restart to use your real model.")


# ============================================================
# ENTROPY CALCULATION  (unchanged from original script)
# ============================================================

def calculate_entropy(password):
    """
    Estimates password entropy based on the possible
    character set used by the password.
    """
    if not password:
        return 0

    charset_size = 0

    if any(c.islower() for c in password):
        charset_size += 26

    if any(c.isupper() for c in password):
        charset_size += 26

    if any(c.isdigit() for c in password):
        charset_size += 10

    if any(c in string.punctuation for c in password):
        charset_size += len(string.punctuation)

    if charset_size == 0:
        return 0

    entropy = len(password) * math.log2(charset_size)

    return entropy



def estimate_crack_time(entropy, guesses_per_second=1_000_000_000):
    """
    Estimates average brute-force crack time.
    Average guesses required ≈ 2^(entropy - 1)
    """
    if entropy <= 0:
        return "Instant"

    possible_passwords = 2 ** entropy
    average_guesses = possible_passwords / 2
    seconds = average_guesses / guesses_per_second

    return format_time(seconds)




def format_time(seconds):

    if seconds < 1:
        return "Less than 1 second"

    if seconds < 60:
        return f"{seconds:.2f} seconds"

    minutes = seconds / 60

    if minutes < 60:
        return f"{minutes:.2f} minutes"

    hours = minutes / 60

    if hours < 24:
        return f"{hours:.2f} hours"

    days = hours / 24

    if days < 365:
        return f"{days:.2f} days"

    years = days / 365

    if years < 1_000:
        return f"{years:.2f} years"

    if years < 1_000_000:
        return f"{years / 1_000:.2f} thousand years"

    if years < 1_000_000_000:
        return f"{years / 1_000_000:.2f} million years"

    if years < 1_000_000_000_000:
        return f"{years / 1_000_000_000:.2f} billion years"

    return f"{years / 1_000_000_000_000:.2f} trillion years"




def analyze_characters(password):
    return {
        "Length": len(password),
        "Uppercase": sum(c.isupper() for c in password),
        "Lowercase": sum(c.islower() for c in password),
        "Digits": sum(c.isdigit() for c in password),
        "Special Characters": sum(c in string.punctuation for c in password),
    }



COMMON_PASSWORDS = [
    "password", "123456", "12345678", "qwerty",
    "admin", "letmein", "welcome",
]


def generate_suggestions(password):
    suggestions = []

    if len(password) < 12:
        suggestions.append("Increase the password length to at least 12 characters.")

    if not any(c.isupper() for c in password):
        suggestions.append("Add uppercase letters.")

    if not any(c.islower() for c in password):
        suggestions.append("Add lowercase letters.")

    if not any(c.isdigit() for c in password):
        suggestions.append("Add numbers.")

    if not any(c in string.punctuation for c in password):
        suggestions.append("Add special characters such as !, @, #, or $.")

    if password.lower() in COMMON_PASSWORDS:
        suggestions.append("Avoid commonly used passwords.")

    return suggestions




def classify_strength(password, entropy):
    """
    Uses the trained ML model if it was loaded successfully.
    Otherwise falls back to a transparent entropy/composition-based
    heuristic so the app is fully functional without the .pkl files.
    """
    if USING_ML_MODEL:
        prediction = model.predict([password])[0]
        strength = encoder.inverse_transform([prediction])[0]
        return str(strength)

    # --- Heuristic fallback ---
    if password.lower() in COMMON_PASSWORDS or entropy == 0:
        return "Very Weak"
    if entropy < 28:
        return "Weak"
    if entropy < 45:
        return "Fair"
    if entropy < 65:
        return "Strong"
    return "Very Strong"




@app.route("/")
def index():
    return render_template("index.html", using_ml_model=USING_ML_MODEL)


@app.route("/api/analyze", methods=["POST"])
def analyze():
    data = request.get_json(silent=True) or {}
    password = data.get("password", "")

    if not password:
        return jsonify({"error": "Please enter a password."}), 400

    entropy = calculate_entropy(password)
    crack_time = estimate_crack_time(entropy)
    analysis = analyze_characters(password)
    suggestions = generate_suggestions(password)
    strength = classify_strength(password, entropy)

    return jsonify({
        "strength": strength,
        "entropy": round(entropy, 2),
        "crack_time": crack_time,
        "analysis": analysis,
        "suggestions": suggestions,
        "using_ml_model": USING_ML_MODEL,
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)

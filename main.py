
import math
import string
import joblib


# ============================================================
# LOAD TRAINED ML MODEL
# ============================================================

try:
    model = joblib.load("password_strength_model.pkl")
    encoder = joblib.load("label_encoder.pkl")

    print("✅ ML model loaded successfully.")

except FileNotFoundError:
    print("❌ Model files not found.")
    print("Make sure these files are in the same folder:")
    print("  password_strength_model.pkl")
    print("  label_encoder.pkl")
    exit()


# ============================================================
# ENTROPY CALCULATION
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


# ============================================================
# CRACK TIME ESTIMATION
# ============================================================

def estimate_crack_time(entropy, guesses_per_second=1_000_000_000):
    """
    Estimates average brute-force crack time.

    guesses_per_second:
        Assumed attacker guessing rate.

    Default:
        1 billion guesses/second.

    Average guesses required ≈ 2^(entropy - 1)
    """

    if entropy <= 0:
        return "Instant"

    possible_passwords = 2 ** entropy

    average_guesses = possible_passwords / 2

    seconds = average_guesses / guesses_per_second

    return format_time(seconds)


# ============================================================
# FORMAT TIME
# ============================================================

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


# ============================================================
# PASSWORD CHARACTER ANALYSIS
# ============================================================

def analyze_characters(password):

    return {
        "Length": len(password),
        "Uppercase": sum(c.isupper() for c in password),
        "Lowercase": sum(c.islower() for c in password),
        "Digits": sum(c.isdigit() for c in password),
        "Special Characters": sum(c in string.punctuation for c in password)
    }


# ============================================================
# SUGGESTIONS
# ============================================================

def generate_suggestions(password):

    suggestions = []

    if len(password) < 12:
        suggestions.append(
            "Increase the password length to at least 12 characters."
        )

    if not any(c.isupper() for c in password):
        suggestions.append(
            "Add uppercase letters."
        )

    if not any(c.islower() for c in password):
        suggestions.append(
            "Add lowercase letters."
        )

    if not any(c.isdigit() for c in password):
        suggestions.append(
            "Add numbers."
        )

    if not any(c in string.punctuation for c in password):
        suggestions.append(
            "Add special characters such as !, @, #, or $."
        )

    common_passwords = [
        "password",
        "123456",
        "12345678",
        "qwerty",
        "admin",
        "letmein",
        "welcome"
    ]

    if password.lower() in common_passwords:
        suggestions.append(
            "Avoid commonly used passwords."
        )

    return suggestions


# ============================================================
# MAIN PROGRAM
# ============================================================

def main():

    print("\n" + "=" * 60)
    print("             AI PASSWORD SECURITY ANALYZER")
    print("=" * 60)

    print("\nCrack-time assumption:")
    print("1 billion guesses per second")
    print("(This is a theoretical brute-force estimate.)")

    while True:

        password = input(
            "\nEnter password to analyze (or type 'exit'): "
        )

        if password.lower() == "exit":
            print("\nExiting...")
            break

        if not password:
            print("❌ Please enter a password.")
            continue

        # ----------------------------------------------------
        # 1. ML PREDICTION
        # ----------------------------------------------------

        prediction = model.predict([password])[0]

        strength = encoder.inverse_transform([prediction])[0]

        # ----------------------------------------------------
        # 2. ENTROPY
        # ----------------------------------------------------

        entropy = calculate_entropy(password)

        # ----------------------------------------------------
        # 3. CRACK TIME
        # ----------------------------------------------------

        crack_time = estimate_crack_time(entropy)

        # ----------------------------------------------------
        # 4. CHARACTER ANALYSIS
        # ----------------------------------------------------

        analysis = analyze_characters(password)

        # ----------------------------------------------------
        # 5. SUGGESTIONS
        # ----------------------------------------------------

        suggestions = generate_suggestions(password)

        # ----------------------------------------------------
        # DISPLAY RESULT
        # ----------------------------------------------------

        print("\n" + "=" * 60)
        print("                PASSWORD ANALYSIS")
        print("=" * 60)

        print(f"\nPassword        : {password}")
        print(f"ML Strength     : {strength}")
        print(f"Entropy         : {entropy:.2f} bits")
        print(f"Estimated Crack : {crack_time}")

        print("\nCharacter Analysis")
        print("-" * 30)

        for name, value in analysis.items():
            print(f"{name:<22}: {value}")

        if suggestions:

            print("\nRecommendations")
            print("-" * 30)

            for suggestion in suggestions:
                print(f"• {suggestion}")

        else:

            print("\n✅ No basic improvements detected.")

        print("\n" + "=" * 60)


# ============================================================
# RUN PROGRAM
# ============================================================

if __name__ == "__main__":
    main()


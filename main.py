import getpass
import mysql.connector


db_config = {
    "host": "localhost",
    "user": "root", 
    "password": "root",  
    "database": "cypbl",  # Replace with your database name
}

connection = mysql.connector.connect(**db_config)
cursor = connection.cursor()

print("Successfully connected to the database.\n")
user_input = getpass.getpass("Enter password to test: ").strip()
query = "SELECT vuln FROM data WHERE password = %s"
cursor.execute(query, (user_input,))
result = cursor.fetchone()
print("-" * 50)
if result:
    vulnerability_description = result[0]
    print("⚠️ VULNERABILITY DETECTED!")
    print(f"Status: Weak / Exposed Password")
    print(f"Details: {vulnerability_description}")
else:
    print("✅ PASSED: Password not found in the weak credentials database.")
print("-" * 50)

# 5. Close connection
cursor.close()
connection.close()
print("\nDatabase connection closed.")
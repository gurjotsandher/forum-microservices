import sys
from passlib.hash import pbkdf2_sha256


# Function to hash the password using PBKDF2 with custom iteration count
def generate_pbkdf2_hash(password, iterations=260000):
    # Generate hash with passlib
    hashed = pbkdf2_sha256.using(rounds=iterations).hash(password)

    # Replace the prefix and return in the format that matches the DB
    return hashed.replace('$pbkdf2-sha256$', 'pbkdf2:sha256')


# Check if the user provided a password argument
if len(sys.argv) != 2:
    print("Usage: python generate_hash.py <password>")
    sys.exit(1)

# Get the password from the command-line argument
password = sys.argv[1]

# Generate the hashed password with the specified iteration count
hashed_password = generate_pbkdf2_hash(password)

# Print the hashed password
print(f"Hash => {hashed_password}")

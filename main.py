import os

password = "admin123"

def login(username, password):
    if username == "admin" and password == "admin123":
        print("Login Success")
    else:
        print("Login Failed")

def add(a,b):
 print(a+b)
 return a+b

login("admin", "admin123")
add(5,6)

print("Webhook Test 2")
print("Automatic Review Test")
print("Webhook Final Test")

def get_user(user_id):
    query = "SELECT * FROM users WHERE id = ?"
    return query, (user_id,)


API_KEY = "my-secret-api-key-12345"

def delete_user(user_id):
    query = "DELETE FROM users WHERE id = ?"
    return query, (user_id,)

def find_user(users, target):
    for user in users:
        if user["name"] == target:
            return user

    return None


def calculate_average(numbers):
    total = 0

    for number in numbers:
        total += number

    return total / len(numbers)

def search_user(user_id):
    query = "SELECT * FROM users WHERE id = ?"
    return query, (user_id,)
def count_active_users(users):
    count = 0
    for user in users:
        if user.get("active"):
            count += 1
    return count


def find_admin(users):
    for user in users:
        if user.get("role") == "admin":
            return user
    return None


def find_moderator(users):
    for user in users:
        if user.get("role") == "moderator":
            return user
    return None

def find_reviewer(users):
    for user in users:
        if user.get("role") == "reviewer":
            return user
    return None

print('Final review validation')
print('Final review validation 2')

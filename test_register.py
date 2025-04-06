import requests

# URLs for routes
register_url = "http://127.0.0.1:5000/register"
login_url = "http://127.0.0.1:5000/login"
create_petition_url = "http://127.0.0.1:5000/create_petition"
view_petitions_url = "http://127.0.0.1:5000/petitions"
sign_petition_url = "http://127.0.0.1:5000/sign_petition/1"
admin_login_url = "http://127.0.0.1:5000/admin/login"
set_threshold_url = "http://127.0.0.1:5000/admin/set_threshold"
admin_view_petitions_url = "http://127.0.0.1:5000/admin/view_petitions"
close_petition_url = "http://127.0.0.1:5000/admin/close_petition/1"

# Test Case 1: Valid Registration
data_valid_registration = {
    "email": "uniqueuser@example.com",
    "name": "Unique User",
    "dob": "1995-01-01",
    "password": "uniquepassword",
    "bio_id": "D05HPPQNJ4"
}

response_valid_registration = requests.post(register_url, json=data_valid_registration)
print("Test Case 1: Valid Registration")
print(f"Status Code: {response_valid_registration.status_code}")
print(f"Response: {response_valid_registration.json()}")

# Test Case 2: Invalid Registration
data_invalid_registration = {
    "email": "invaliduser@example.com",
    "name": "Invalid User",
    "dob": "1990-01-01",
    "password": "invalidpassword",
    "bio_id": "INVALID123"
}

response_invalid_registration = requests.post(register_url, json=data_invalid_registration)
print("\nTest Case 2: Invalid Registration")
print(f"Status Code: {response_invalid_registration.status_code}")
print(f"Response: {response_invalid_registration.json()}")

# Test Case 3: Successful Login
login_data_valid = {
    "email": "uniqueuser@example.com",
    "password": "uniquepassword"
}

response_login_valid = requests.post(login_url, json=login_data_valid)
print("\nTest Case 3: Successful Login")
print(f"Status Code: {response_login_valid.status_code}")
print(f"Response: {response_login_valid.json()}")

# Test Case 5: Create Petition
session_token = None
if response_login_valid.status_code == 200:
    session_token = response_login_valid.cookies.get('session')
    headers = {'Cookie': f'session={session_token}'}
    data_create_petition = {
        "email": "uniqueuser@example.com",
        "title": "Reduce Plastic Usage",
        "content": "This petition aims to reduce single-use plastics."
    }
    response_create_petition = requests.post(create_petition_url, json=data_create_petition, headers=headers)
    print("\nTest Case 5: Create Petition")
    print(f"Status Code: {response_create_petition.status_code}")
    print(f"Response: {response_create_petition.json()}")

# Test Case 6: View Petitions
response_view_petitions = requests.get(view_petitions_url, headers=headers)
print("\nTest Case 6: View Petitions")
print(f"Status Code: {response_view_petitions.status_code}")
print(f"Response: {response_view_petitions.json()}")

# Test Case 7: Sign Petition
response_sign_petition = requests.post(sign_petition_url, headers=headers)
print("\nTest Case 7: Sign Petition")
print(f"Status Code: {response_sign_petition.status_code}")
print(f"Response: {response_sign_petition.json()}")

# Test Case 8: Admin Login
admin_login_data = {
    "email": "admin@petition.parliament.sr",
    "password": "2025%shangrila"
}

response_admin_login = requests.post(admin_login_url, json=admin_login_data)
print("\nTest Case 8: Admin Login")
print(f"Status Code: {response_admin_login.status_code}")
print(f"Response: {response_admin_login.json()}")

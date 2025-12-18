"""

Test script for NotificationService
This script tests all endpoints of the notification microservice.
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8083"

def test_health_check():
    """Test the health check endpoint"""
    print("\n=== Testing Health Check ===")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_request_created():
    """Test the request created notification endpoint"""
    print("\n=== Testing Request Created Notification ===")
    payload = {
        "requestId": 123,
        "ownerId": 456,
        "ownerEmail": "pasaroiumihai@yahoo.com",  # Change this to your test email
        "ownerName": "John Doe",
        "status": "PENDING",
        "serviceType": "MAINTENANCE",
        "priority": "HIGH",
        "requestedFrom": "2024-01-15T10:00:00",
        "requestedTo": "2024-01-15T12:00:00"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/notifications/request-created",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        print(f"Response text: {response.text if 'response' in locals() else 'No response'}")
        return False

def test_request_updated():
    """Test the request updated notification endpoint"""
    print("\n=== Testing Request Updated Notification ===")
    payload = {
        "requestId": 123,
        "ownerId": 456,
        "ownerEmail": "pasaroiumihai@yahoo.com",  # Change this to your test email
        "ownerName": "John Doe",
        "newStatus": "IN_PROGRESS",
        "mechanicNotes": "Replaced brake pads and checked brake fluid levels",
        "totalCost": 150.00,
        "partsUsed": "Brake pads, brake fluid"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/notifications/request-updated",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        print(f"Response text: {response.text if 'response' in locals() else 'No response'}")
        return False

def test_status_changed():
    """Test the status changed notification endpoint"""
    print("\n=== Testing Status Changed Notification ===")
    payload = {
        "requestId": 123,
        "ownerId": 456,
        "ownerEmail": "pasaroiumihai@yahoo.com",  # Change this to your test email
        "ownerName": "John Doe",
        "newStatus": "COMPLETED"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/notifications/status-changed",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        print(f"Response text: {response.text if 'response' in locals() else 'No response'}")
        return False

def test_validation_errors():
    """Test validation error handling"""
    print("\n=== Testing Validation Errors ===")
    
    # Test with missing required fields
    payload = {
        "requestId": 123
        # Missing ownerEmail, ownerName, etc.
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/notifications/request-created",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 400
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("NotificationService Test Suite")
    print("=" * 50)
    print("\nMake sure the service is running on http://localhost:8083")
    print("Update the email addresses in the test payloads to your test email!")
    
    input("\nPress Enter to start testing...")
    
    results = []
    results.append(("Health Check", test_health_check()))
    results.append(("Request Created", test_request_created()))
    results.append(("Request Updated", test_request_updated()))
    results.append(("Status Changed", test_status_changed()))
    results.append(("Validation Errors", test_validation_errors()))
    
    print("\n" + "=" * 50)
    print("Test Results Summary")
    print("=" * 50)
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(result[1] for result in results)
    print("\n" + "=" * 50)
    if all_passed:
        print("All tests passed! ✓")
    else:
        print("Some tests failed. Check the output above.")
    print("=" * 50)

if __name__ == "__main__":
    main()


import requests
import subprocess
import os
import sys
import urllib3
import json

# Disable SSL-related warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def main():
    host = "https://127.0.0.1:8080"
    # Check if the SSL certificate and key files exist
    if not os.path.exists("minh-ngu.crt") or not os.path.exists("minh-ngu.key"):
        # Generate SSL certificate and key
        try:
            result = subprocess.run("openssl req -newkey rsa:4096 -x509 -sha256 -days 365 \
                -nodes -out minh-ngu.crt -keyout minh-ngu.key \
                -subj \"/C=FR/ST=Paris/L=Paris/O=42 School/OU=minh-ngu/CN=minh-ngu/\"",
                shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            print("SSL certificate and key files generated successfully!")
        except subprocess.CalledProcessError as e:
            print("Failed to generate SSL certificate and key files. Error:", e)
            return 1

    # login = input("Login: ")
    # password = getpass.getpass("Password: ")
    login = "admin"
    password = "admin"

    try:
        # Include CSRF token in the data for the POST request
        response = requests.post(host + "/log_in/",
                                data={"login": login, "password": password}, 
                                cert=("minh-ngu.crt", "minh-ngu.key"),
                                verify=False)

        if response.status_code != 200:
            print("Request failed with status code:", response.status_code)

    except requests.exceptions.SSLError as e:
        print("SSL Certificate verification failed. Error:", e)
        return 1
    except requests.exceptions.RequestException as e:  
        print("Request failed. Error:", e)
        return 1
    try:
        response = requests.get(host + "/game/update",
            cert=("minh-ngu.crt", "minh-ngu.key"), verify=False)
        if response.status_code != 200:
            print("Request failed with status code:", response.status_code)
    except requests.exceptions.RequestException as e:  
        print("Request failed. Error:", e)
        return 1
    rooms = json.loads(response.text)
    print("Rooms: ", rooms)

if __name__ == "__main__":
    exit_code = main()
    os.remove("minh-ngu.crt")
    os.remove("minh-ngu.key")
    sys.exit(exit_code)
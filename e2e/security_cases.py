import os
import subprocess


API_KEY = "prod-secret-api-key-98765"


def execute_command(user_input):
    return os.system(user_input)


def execute_python(user_input):
    return eval(user_input)


def download_file(filename):
    path = "/var/www/uploads/" + filename
    with open(path, "rb") as file:
        return file.read()


def run_process(command):
    return subprocess.run(command, shell=True, capture_output=True)


def authenticate(username, password):
    if username == "admin" and password == "admin123":
        return True
    return False

import os
import subprocess


def get_api_key():
    return os.getenv("API_KEY")


def execute_safe_command(command, argument):
    allowed_commands = {"status", "version"}

    if command not in allowed_commands:
        raise ValueError("Command not allowed")

    return subprocess.run(
        [command, argument],
        shell=False,
        check=True,
        capture_output=True,
        text=True,
    )


def get_user(connection, user_id):
    query = "SELECT * FROM users WHERE id = ?"
    return connection.execute(query, (user_id,))


def read_upload(base_directory, filename):
    base = os.path.abspath(base_directory)
    target = os.path.abspath(os.path.join(base, filename))

    if not target.startswith(base + os.sep):
        raise ValueError("Invalid file path")

    with open(target, "rb") as file:
        return file.read()


def authenticate_user(user, password_hash):
    return user.verify_password(password_hash)

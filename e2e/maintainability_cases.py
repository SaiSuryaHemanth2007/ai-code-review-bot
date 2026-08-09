def find_admin(users):
    for user in users:
        if user.get("role") == "admin":
            return user
    return None


def find_manager(users):
    for user in users:
        if user.get("role") == "manager":
            return user
    return None


def process_records(records):
    result = []

    for record in records:
        if record.get("active"):
            if record.get("verified"):
                if record.get("score", 0) > 50:
                    if record.get("country") == "IN":
                        result.append(record)

    debug_value = "temporary"
    print("DEBUG:", result)

    return result

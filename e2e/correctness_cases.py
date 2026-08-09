def calculate_average(numbers):
    return sum(numbers) / len(numbers)


def calculate_ratio(total, count):
    return total / count


def get_user(users, user_id):
    for user in users:
        if user["id"] == user_id:
            return user


def update_balance(account, amount):
    account["balance"] += amount
    return account


def append_item(item, items=[]):
    items.append(item)
    return items

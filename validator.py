def validate(user_data: dict) -> dict:

    errors = {}

    for key, value in user_data.items():
        if not value:
            errors[key] = f"{key} can't be blank!"
    return errors

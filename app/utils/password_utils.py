import re

def password_complexity(password: str, username: str, email: str) -> dict:
    pattern_uppercase = re.compile(r'[A-Z]')
    pattern_lowercase = re.compile(r'[a-z]')
    pattern_digit = re.compile(r'\d')
    pattern_special = re.compile(r'[!@#$%^&*(),.?":{}|<>]')
    pattern_username = re.compile(re.escape(username), re.IGNORECASE)
    pattern_email = re.compile(re.escape(email.split('@')[0]), re.IGNORECASE)
    pattern_simple_sequences = re.compile(r'(qwer|asd|zxc|123|abcd|password)', re.IGNORECASE)
    
    complexity = {
        "length": len(password) >= 8,
        "uppercase": bool(pattern_uppercase.search(password)),
        "lowercase": bool(pattern_lowercase.search(password)),
        "digit": bool(pattern_digit.search(password)),
        "special": bool(pattern_special.search(password)),
        "username_in_password": bool(pattern_username.search(password)),
        "email_in_password": bool(pattern_email.search(password)),
        "simple_sequences": bool(pattern_simple_sequences.search(password)),
    }

    complexity["strong"] = complexity["length"] and complexity["uppercase"] and complexity["lowercase"] and (complexity["digit"] or complexity["special"]) and not (complexity["username_in_password"] or complexity["email_in_password"] or complexity["simple_sequences"])
    strong_percentage = 0
    if complexity["length"]:
        strong_percentage += 20
    if complexity["uppercase"]:
        strong_percentage += 20
    if complexity["lowercase"]:
        strong_percentage += 20
    if complexity["digit"]:
        strong_percentage += 20
    if complexity["special"]:
        strong_percentage += 20
    if complexity["username_in_password"]:
        strong_percentage -= 40
    if complexity["email_in_password"]:
        strong_percentage -= 40
    if complexity["simple_sequences"]:
        strong_percentage -= 40
    strong_percentage = max(0, min(100, strong_percentage))
    complexity["strong_percentage"] = strong_percentage
    return complexity

# print(password_complexity("94937wf@Sevqwe123user", username="user123", email="used@example.com"))

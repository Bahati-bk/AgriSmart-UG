from flask import current_app

def send_sms(phone, message):
    provider = current_app.config.get("SMS_PROVIDER", "console")

    if provider == "console":
        print(f"[SMS to {phone}] {message}")
        return True

    # Add real provider integration later
    # Example: requests.post(...) for Africa's Talking, Twilio, etc.
    return False
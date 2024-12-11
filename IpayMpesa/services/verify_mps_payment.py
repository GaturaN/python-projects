import requests
import hmac
import hashlib
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Helper function to delay execution
def delay(ms):
    time.sleep(ms / 1000.0)

# Helper function to create HMAC hash
def create_hash(oid, vid, secret_key):
    data_string = f"{oid}{vid}"
    return hmac.new(
        secret_key.encode(),
        data_string.encode(),
        hashlib.sha256
    ).hexdigest()

# Isolate the API call to a separate function
def make_verification_call(verification_payload):
    response = requests.post(
        'https://apis.ipayafrica.com/payments/v2/transaction/search',
        data=verification_payload,
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )
    response.raise_for_status()  # Raise error for bad status codes
    return response

# Handle payment verification
def verify_mpesa_payment(oid, type, phone, vid, secret_key):
    max_retries = 30
    initial_delay = 4000  # in milliseconds
    retry_delay = 2000  # in milliseconds

    # Initial delay before starting the verification
    delay(initial_delay)

    hash_value = create_hash(oid, vid, secret_key)
    verification_payload = {
        'vid': vid,
        'hash': hash_value,
        'oid': oid
    }

    attempt = 0
    success = False

    while attempt < max_retries and not success:
        try:
            attempt += 1
            logger.info(f"Attempt {attempt}: Verifying payment...")

            # Make the verification call
            verification_response = make_verification_call(verification_payload)

            if verification_response.status_code == 200:
                logger.info("Payment verified successfully.")
                success = True

                data = verification_response.json().get('data', {})
                transaction_code = data.get('transaction_code')
                transaction_amount = data.get('transaction_amount')

                return verification_response.json()
            else:
                logger.warning(
                    f"Attempt {attempt}: Payment not found (status {verification_response.status_code}). Retrying..."
                )
                delay(retry_delay)
        except requests.RequestException as error:
            error_message = (
                error.response.json().get('message')
                if error.response is not None else str(error)
            )
            logger.error(
                f"Attempt {attempt}: Failed due to an error: {error_message}\nRetrying..."
            )
            delay(retry_delay)
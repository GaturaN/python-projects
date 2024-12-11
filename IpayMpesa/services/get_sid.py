import requests
import hmac
import hashlib
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_sid(vid: str, secret_key: str, amount: str, oid: str, phone: str) -> dict:
    try:
        inv = oid

        # Customer's email address
        eml = 'tech.kwaj@gmail.com'
        # Callback URL for payment status
        cbk = ''

        # Set to '1' for live mode, '0' for demo
        live = '1'
        # Default currency
        curr = 'KES'
        # Allow customer to receive transaction notifications
        cst = '0'
        # Default to '0' for HTTP/HTTPS callback
        crl = '0'

        # Generate the data string for hashing
        data_string = f"{live}{oid}{inv}{amount}{phone}{eml}{vid}{curr}{cst}{cbk}"

        # Generate the hash using HMAC SHA-256
        hash_value = hmac.new(
            secret_key.encode(),
            data_string.encode(),
            hashlib.sha256
        ).hexdigest()

        # Prepare the transaction payload
        transaction_payload = {
            'live': live,
            'oid': oid,
            'inv': inv,
            'amount': amount,
            'tel': phone,
            'eml': eml,
            'vid': vid,
            'curr': curr,
            'cbk': cbk,
            'cst': cst,
            'crl': crl,
            'hash': hash_value,
        }

        # Send the POST request
        response = requests.post(
            'https://apis.ipayafrica.com/payments/v2/transact',
            data=transaction_payload,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )

        response.raise_for_status()  # Raise HTTPError for bad responses
        logger.info("SID served successfully")
        return response.json()
    except requests.RequestException as error:
        logger.error("Error getting SID: %s", error)
        raise RuntimeError("Error getting SID") from error
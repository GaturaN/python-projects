import logging
# from config import config
from services.get_sid import get_sid
from services.trigger_stk_push import trigger_stk_push
from services.verify_mps_payment import verify_mpesa_payment

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

phone = '254707'
user_id = '123'
amount = '1'
oid = '1234'



def lipana_mpesa(user_id, phone, amount, oid, type):
    # ipay = config['ipay']
    vid = "buox"
    secret_key = "&X*Sv" 
                
    if not secret_key or not vid:
        raise ValueError("Secret key or vendor ID not set")

    try:
        # Helper function to get session ID (initiate payment session)
        response = get_sid(vid, secret_key, amount, oid, phone)
        sid = response.get('data', {}).get('sid')

        if not sid:
            raise ValueError("Failed to retrieve session ID")

        # Trigger SIM Toolkit (STK PUSH)
        stk_response = trigger_stk_push(phone, sid, vid, secret_key)

        # Verify the payment made by the STK PUSH Triggered
        if stk_response.get('header_status') == 200:
            logger.info("Verifying payment...")

            verification_response = verify_mpesa_payment(oid, type, phone, vid, secret_key)

            # Check for edge cases in the verification response
            if not verification_response:
                raise ValueError("Payment verification failed")

            if verification_response.get('header_status') != 200:
                raise ValueError("Payment verification unsuccessful")

            data = verification_response.get('data', {})
            response_data = {
                'order_id': data.get('oid'),
                'transaction_amount': data.get('transaction_amount'),
                'transaction_code': data.get('transaction_code'),
                'payment_mode': data.get('payment_mode'),
                'paid_at': data.get('paid_at'),
                'telephone': data.get('telephone'),
            }

            return response_data
        else:
            raise ValueError("Failed to initiate payment")
    except Exception as error:
        logger.error("An error occurred during the payment process: %s", error)
        raise RuntimeError("An error occurred during the payment process")
    
# Calling the function when the script runs
if __name__ == "__main__":
    try:
        result = lipana_mpesa(user_id, phone, amount, oid, 'cart')
        logger.info(f"Payment process completed successfully: {result}")
    except Exception as e:
        logger.error(f"Payment process failed: {e}")

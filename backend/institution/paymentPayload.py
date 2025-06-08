import uuid
from django.conf import settings
from institution.models import Plan
from users.models import User


def get_payment_payload(plan_id: str, institution: User, redirection_url: str) -> dict:
    print(institution)
    credit_price = float(Plan.objects.get(id=plan_id).credit_price)
    currency = Plan.objects.get(id=plan_id).currency
    amount = credit_price * institution['credits']

    payload = {
        'amount': int(amount * 100),
        'currency': currency,
        "payment_methods": [
            4877887,
            4877830
        ],
        "items": [
            {
                "name": "Credits",
                "amount": int(credit_price * 100),
                "description": "Innovate Credits",
                "quantity": institution['credits'],
            }
        ],
        "billing_data": {
            "first_name": institution['name'],
            "last_name": institution['name'],
            "email": institution['email'],
            "phone_number": "+201007137947",
        },
        "extras": {
            "plan_id": plan_id
        },
        # "special_reference": str(uuid.uuid4()),
        "redirection_url": redirection_url,
        "expiration": 3600
    }

    return payload

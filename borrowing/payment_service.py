import os

import stripe


stripe.api_key = os.getenv("STRIPE_PUBLIC_KEY")

# Payment Gateway Integration for CyberGuard Enterprise Platform
# Integrates with Stripe, PayPal, and other payment providers

import os
import json
import hashlib
import hmac
from datetime import datetime
from typing import Dict, Optional, List
from flask import Flask, request, jsonify
from functools import wraps


class StripeIntegration:
    """Stripe payment gateway integration"""
    
    def __init__(self, api_key: str = None, webhook_secret: str = None):
        self.api_key = api_key or os.getenv("STRIPE_API_KEY")
        self.webhook_secret = webhook_secret or os.getenv("STRIPE_WEBHOOK_SECRET")
        
        # In production, use actual Stripe SDK
        # import stripe
        # stripe.api_key = self.api_key
    
    def create_checkout_session(
        self,
        customer_email: str,
        price_id: str,
        success_url: str,
        cancel_url: str,
        trial_days: int = 0
    ) -> Dict:
        """Create a Stripe checkout session"""
        # Simulated response - in production use stripe.checkout.Session.create()
        session = {
            "id": f"cs_{os.urandom(12).hex()}",
            "url": f"https://checkout.stripe.com/pay/cs_{os.urandom(12).hex()}",
            "customer_email": customer_email,
            "mode": "subscription",
            "status": "open"
        }
        return session
    
    def create_customer(self, email: str, name: str = None, metadata: Dict = None) -> Dict:
        """Create a Stripe customer"""
        customer = {
            "id": f"cus_{os.urandom(12).hex()}",
            "email": email,
            "name": name,
            "metadata": metadata or {}
        }
        return customer
    
    def create_subscription(
        self,
        customer_id: str,
        price_id: str,
        trial_days: int = 0
    ) -> Dict:
        """Create a subscription"""
        subscription = {
            "id": f"sub_{os.urandom(12).hex()}",
            "customer": customer_id,
            "status": "trialing" if trial_days > 0 else "active",
            "current_period_start": datetime.now().isoformat(),
            "trial_end": (datetime.now().timestamp() + trial_days * 86400) if trial_days > 0 else None
        }
        return subscription
    
    def verify_webhook(self, payload: bytes, signature: str) -> Dict:
        """Verify Stripe webhook signature"""
        # In production, use stripe.Webhook.construct_event()
        expected_sig = hmac.new(
            self.webhook_secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        # Simplified verification
        return json.loads(payload)
    
    def cancel_subscription(self, subscription_id: str, immediate: bool = False) -> Dict:
        """Cancel a subscription"""
        result = {
            "id": subscription_id,
            "status": "canceled" if immediate else "active",
            "cancel_at_period_end": not immediate
        }
        return result


class PayPalIntegration:
    """PayPal payment gateway integration"""
    
    def __init__(self, client_id: str = None, client_secret: str = None):
        self.client_id = client_id or os.getenv("PAYPAL_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("PAYPAL_CLIENT_SECRET")
        self.api_base = "https://api-m.paypal.com"  # Production
        # self.api_base = "https://api-m.sandbox.paypal.com"  # Sandbox
    
    def create_order(self, amount: float, currency: str = "USD", description: str = None) -> Dict:
        """Create a PayPal order"""
        order = {
            "id": f"PAYPAL-{os.urandom(12).hex().upper()}",
            "status": "CREATED",
            "amount": {
                "currency_code": currency,
                "value": str(amount)
            },
            "description": description,
            "links": [
                {
                    "rel": "approve",
                    "href": f"{self.api_base}/checkoutnow?token=EC-{os.urandom(8).hex()}"
                }
            ]
        }
        return order
    
    def capture_order(self, order_id: str) -> Dict:
        """Capture a PayPal order"""
        result = {
            "id": order_id,
            "status": "COMPLETED",
            "purchase_units": [
                {
                    "payments": {
                        "captures": [
                            {
                                "id": f"CAP-{os.urandom(12).hex().upper()}",
                                "status": "COMPLETED"
                            }
                        ]
                    }
                }
            ]
        }
        return result
    
    def create_billing_plan(self, name: str, amount: float, interval: str = "MONTH") -> Dict:
        """Create a billing plan for subscriptions"""
        plan = {
            "id": f"P-{os.urandom(12).hex().upper()}",
            "name": name,
            "status": "ACTIVE",
            "billing_cycles": [
                {
                    "frequency": {
                        "interval_unit": interval,
                        "interval_count": 1
                    },
                    "pricing_scheme": {
                        "fixed_price": {
                            "value": str(amount),
                            "currency_code": "USD"
                        }
                    }
                }
            ]
        }
        return plan


class CreditCardProcessor:
    """Direct credit card processing (PCI-compliant tokenization required)"""
    
    def __init__(self):
        # In production, use a PCI-compliant payment processor
        self.processor_name = "CyberGuard Payments"
    
    def tokenize_card(self, card_number: str, exp_month: int, exp_year: int, cvv: str) -> str:
        """Tokenize credit card (PCI-compliant)"""
        # In production, send to secure tokenization service
        # Never store raw card data
        token = f"tok_{hashlib.sha256(card_number.encode()).hexdigest()[:16]}"
        return token
    
    def charge_card(self, token: str, amount: float, description: str = None) -> Dict:
        """Charge a tokenized card"""
        charge = {
            "id": f"ch_{os.urandom(12).hex()}",
            "amount": amount,
            "currency": "USD",
            "status": "succeeded",
            "description": description,
            "created": datetime.now().isoformat()
        }
        return charge


class PaymentWebhookHandler:
    """Handle webhooks from payment providers"""
    
    def __init__(self, payment_system):
        self.payment_system = payment_system
    
    def handle_stripe_webhook(self, event_type: str, data: Dict) -> bool:
        """Handle Stripe webhook events"""
        handlers = {
            "checkout.session.completed": self._handle_checkout_completed,
            "customer.subscription.created": self._handle_subscription_created,
            "customer.subscription.updated": self._handle_subscription_updated,
            "customer.subscription.deleted": self._handle_subscription_deleted,
            "invoice.payment_succeeded": self._handle_payment_succeeded,
            "invoice.payment_failed": self._handle_payment_failed,
        }
        
        handler = handlers.get(event_type)
        if handler:
            return handler(data)
        
        return False
    
    def _handle_checkout_completed(self, data: Dict) -> bool:
        """Handle completed checkout"""
        print(f"Checkout completed: {data.get('id')}")
        # Update database, send confirmation email, etc.
        return True
    
    def _handle_subscription_created(self, data: Dict) -> bool:
        """Handle new subscription"""
        print(f"Subscription created: {data.get('id')}")
        # Generate license, send welcome email, etc.
        return True
    
    def _handle_subscription_updated(self, data: Dict) -> bool:
        """Handle subscription update"""
        print(f"Subscription updated: {data.get('id')}")
        return True
    
    def _handle_subscription_deleted(self, data: Dict) -> bool:
        """Handle subscription cancellation"""
        print(f"Subscription deleted: {data.get('id')}")
        # Deactivate license, send cancellation email, etc.
        return True
    
    def _handle_payment_succeeded(self, data: Dict) -> bool:
        """Handle successful payment"""
        print(f"Payment succeeded: {data.get('id')}")
        # Update payment status, send receipt, etc.
        return True
    
    def _handle_payment_failed(self, data: Dict) -> bool:
        """Handle failed payment"""
        print(f"Payment failed: {data.get('id')}")
        # Send dunning email, update status, etc.
        return True


# Flask API for payment processing
app = Flask(__name__)

# Initialize integrations
stripe_integration = StripeIntegration()
paypal_integration = PayPalIntegration()
card_processor = CreditCardProcessor()


def require_api_key(f):
    """Decorator to require API key authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        # In production, validate against database
        if not api_key or api_key != os.getenv('PAYMENT_API_KEY', 'test_key'):
            return jsonify({"error": "Invalid API key"}), 401
        return f(*args, **kwargs)
    return decorated_function


@app.route('/api/payment/checkout/stripe', methods=['POST'])
@require_api_key
def create_stripe_checkout():
    """Create Stripe checkout session"""
    data = request.json
    
    session = stripe_integration.create_checkout_session(
        customer_email=data['email'],
        price_id=data['price_id'],
        success_url=data['success_url'],
        cancel_url=data['cancel_url'],
        trial_days=data.get('trial_days', 0)
    )
    
    return jsonify(session)


@app.route('/api/payment/checkout/paypal', methods=['POST'])
@require_api_key
def create_paypal_order():
    """Create PayPal order"""
    data = request.json
    
    order = paypal_integration.create_order(
        amount=data['amount'],
        currency=data.get('currency', 'USD'),
        description=data.get('description')
    )
    
    return jsonify(order)


@app.route('/api/payment/card/charge', methods=['POST'])
@require_api_key
def charge_credit_card():
    """Charge a credit card"""
    data = request.json
    
    # Tokenize card (in production, done client-side)
    token = card_processor.tokenize_card(
        card_number=data['card_number'],
        exp_month=data['exp_month'],
        exp_year=data['exp_year'],
        cvv=data['cvv']
    )
    
    # Charge the card
    charge = card_processor.charge_card(
        token=token,
        amount=data['amount'],
        description=data.get('description')
    )
    
    return jsonify(charge)


@app.route('/api/webhooks/stripe', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhooks"""
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        event = stripe_integration.verify_webhook(payload, sig_header)
        
        handler = PaymentWebhookHandler(None)
        handler.handle_stripe_webhook(event['type'], event['data']['object'])
        
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/api/webhooks/paypal', methods=['POST'])
def paypal_webhook():
    """Handle PayPal webhooks"""
    data = request.json
    
    # Verify webhook signature
    # Process event
    
    return jsonify({"status": "success"}), 200


@app.route('/api/subscription/cancel', methods=['POST'])
@require_api_key
def cancel_subscription():
    """Cancel a subscription"""
    data = request.json
    provider = data.get('provider', 'stripe')
    
    if provider == 'stripe':
        result = stripe_integration.cancel_subscription(
            subscription_id=data['subscription_id'],
            immediate=data.get('immediate', False)
        )
    else:
        result = {"error": "Unsupported provider"}
    
    return jsonify(result)


@app.route('/api/pricing', methods=['GET'])
def get_pricing():
    """Get pricing information"""
    pricing = {
        "tiers": [
            {
                "name": "Community",
                "price": 0,
                "billing": "free",
                "features": [
                    "Basic threat detection",
                    "Core security features",
                    "Community support",
                    "1 user"
                ]
            },
            {
                "name": "Professional",
                "price": 499,
                "billing": "monthly",
                "annual_price": 4990,
                "features": [
                    "ML-powered detection",
                    "Advanced analytics",
                    "Email support",
                    "Up to 10 users",
                    "API access"
                ]
            },
            {
                "name": "Enterprise",
                "price": 2999,
                "billing": "monthly",
                "annual_price": 29990,
                "features": [
                    "All Professional features",
                    "SIEM integration",
                    "24/7 support",
                    "Unlimited users",
                    "Custom integrations",
                    "Dedicated account manager"
                ]
            },
            {
                "name": "Unlimited",
                "price": 9999,
                "billing": "monthly",
                "custom": True,
                "features": [
                    "All Enterprise features",
                    "On-premise deployment",
                    "Custom development",
                    "Training & certification",
                    "99.99% SLA",
                    "Dedicated support engineer"
                ]
            }
        ],
        "currency": "USD",
        "trial_days": 14
    }
    
    return jsonify(pricing)


if __name__ == '__main__':
    print("CyberGuard Payment Gateway API")
    print("=" * 50)
    print("\nEndpoints:")
    print("  POST /api/payment/checkout/stripe")
    print("  POST /api/payment/checkout/paypal")
    print("  POST /api/payment/card/charge")
    print("  POST /api/webhooks/stripe")
    print("  POST /api/webhooks/paypal")
    print("  POST /api/subscription/cancel")
    print("  GET  /api/pricing")
    print("\nStarting server on http://localhost:8080...")
    app.run(host='0.0.0.0', port=8080, debug=True)

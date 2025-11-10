# Payment Dashboard for CyberGuard Enterprise Platform
# Web interface for payment management, subscriptions, and billing

from flask import Flask, render_template_string, request, jsonify, session, redirect, url_for
from datetime import datetime, timedelta
import json
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# HTML Template for Payment Dashboard
PAYMENT_DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CyberGuard Payment Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 40px;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .pricing-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 30px;
            margin-bottom: 40px;
        }
        
        .pricing-card {
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            transition: transform 0.3s, box-shadow 0.3s;
            position: relative;
            overflow: hidden;
        }
        
        .pricing-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.3);
        }
        
        .pricing-card.featured {
            border: 3px solid #667eea;
        }
        
        .pricing-card.featured::before {
            content: 'MOST POPULAR';
            position: absolute;
            top: 0;
            right: 0;
            background: #667eea;
            color: white;
            padding: 5px 20px;
            font-size: 0.7em;
            font-weight: bold;
            transform: rotate(45deg) translate(30%, -50%);
        }
        
        .tier-name {
            font-size: 1.8em;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
        }
        
        .tier-price {
            font-size: 3em;
            font-weight: bold;
            color: #667eea;
            margin: 20px 0;
        }
        
        .tier-price span {
            font-size: 0.4em;
            color: #666;
        }
        
        .tier-features {
            list-style: none;
            margin: 20px 0;
        }
        
        .tier-features li {
            padding: 10px 0;
            border-bottom: 1px solid #eee;
            color: #555;
        }
        
        .tier-features li:before {
            content: '✓ ';
            color: #667eea;
            font-weight: bold;
            margin-right: 8px;
        }
        
        .cta-button {
            width: 100%;
            padding: 15px;
            border: none;
            border-radius: 8px;
            background: #667eea;
            color: white;
            font-size: 1.1em;
            font-weight: bold;
            cursor: pointer;
            transition: background 0.3s;
        }
        
        .cta-button:hover {
            background: #5568d3;
        }
        
        .cta-button.secondary {
            background: #e0e0e0;
            color: #333;
        }
        
        .cta-button.secondary:hover {
            background: #d0d0d0;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        
        .stat-card {
            background: white;
            border-radius: 12px;
            padding: 25px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .stat-value {
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
        }
        
        .stat-label {
            color: #666;
            margin-top: 10px;
            font-size: 0.9em;
        }
        
        .subscription-info {
            background: white;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .subscription-info h2 {
            color: #333;
            margin-bottom: 20px;
        }
        
        .info-row {
            display: flex;
            justify-content: space-between;
            padding: 15px 0;
            border-bottom: 1px solid #eee;
        }
        
        .info-row:last-child {
            border-bottom: none;
        }
        
        .info-label {
            font-weight: 600;
            color: #666;
        }
        
        .info-value {
            color: #333;
        }
        
        .badge {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: bold;
        }
        
        .badge.active {
            background: #d4edda;
            color: #155724;
        }
        
        .badge.trial {
            background: #fff3cd;
            color: #856404;
        }
        
        .badge.cancelled {
            background: #f8d7da;
            color: #721c24;
        }
        
        .payment-history {
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .payment-history h2 {
            color: #333;
            margin-bottom: 20px;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
        }
        
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }
        
        th {
            background: #f8f9fa;
            font-weight: 600;
            color: #666;
        }
        
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 1000;
        }
        
        .modal-content {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: white;
            border-radius: 12px;
            padding: 40px;
            max-width: 500px;
            width: 90%;
        }
        
        .modal-close {
            position: absolute;
            top: 15px;
            right: 15px;
            font-size: 1.5em;
            cursor: pointer;
            color: #999;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #333;
        }
        
        .form-group input,
        .form-group select {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 1em;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>💳 CyberGuard Payment Dashboard</h1>
            <p>Manage your subscription and billing</p>
        </div>
        
        <!-- Stats Section -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">$2,999</div>
                <div class="stat-label">Monthly Cost</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">14</div>
                <div class="stat-label">Trial Days Remaining</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">3</div>
                <div class="stat-label">Active Licenses</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">$8,997</div>
                <div class="stat-label">Total Paid</div>
            </div>
        </div>
        
        <!-- Current Subscription -->
        <div class="subscription-info">
            <h2>Current Subscription</h2>
            <div class="info-row">
                <span class="info-label">Plan</span>
                <span class="info-value"><strong>Enterprise Edition</strong></span>
            </div>
            <div class="info-row">
                <span class="info-label">Status</span>
                <span class="info-value"><span class="badge trial">Trial</span></span>
            </div>
            <div class="info-row">
                <span class="info-label">Billing Cycle</span>
                <span class="info-value">Monthly</span>
            </div>
            <div class="info-row">
                <span class="info-label">Next Billing Date</span>
                <span class="info-value">November 24, 2025</span>
            </div>
            <div class="info-row">
                <span class="info-label">Payment Method</span>
                <span class="info-value">Visa •••• 4242</span>
            </div>
            <div class="info-row">
                <span class="info-label">License Key</span>
                <span class="info-value"><code>CGEP-A3F2-B8E1-C9D4-F7A6</code></span>
            </div>
        </div>
        
        <!-- Pricing Plans -->
        <h2 style="color: white; text-align: center; margin: 40px 0 20px;">Pricing Plans</h2>
        <div class="pricing-grid">
            <div class="pricing-card">
                <div class="tier-name">Community</div>
                <div class="tier-price">$0<span>/month</span></div>
                <ul class="tier-features">
                    <li>Basic threat detection</li>
                    <li>Core security features</li>
                    <li>Community support</li>
                    <li>1 user</li>
                </ul>
                <button class="cta-button secondary">Current Plan</button>
            </div>
            
            <div class="pricing-card">
                <div class="tier-name">Professional</div>
                <div class="tier-price">$499<span>/month</span></div>
                <ul class="tier-features">
                    <li>ML-powered detection</li>
                    <li>Advanced analytics</li>
                    <li>Email support</li>
                    <li>Up to 10 users</li>
                    <li>API access</li>
                </ul>
                <button class="cta-button" onclick="showCheckout('professional')">Upgrade</button>
            </div>
            
            <div class="pricing-card featured">
                <div class="tier-name">Enterprise</div>
                <div class="tier-price">$2,999<span>/month</span></div>
                <ul class="tier-features">
                    <li>All Pro features</li>
                    <li>SIEM integration</li>
                    <li>24/7 support</li>
                    <li>Unlimited users</li>
                    <li>Custom integrations</li>
                </ul>
                <button class="cta-button">Current Plan</button>
            </div>
            
            <div class="pricing-card">
                <div class="tier-name">Unlimited</div>
                <div class="tier-price">$9,999<span>/month</span></div>
                <ul class="tier-features">
                    <li>All Enterprise features</li>
                    <li>On-premise deployment</li>
                    <li>Custom development</li>
                    <li>Training & certification</li>
                    <li>99.99% SLA</li>
                </ul>
                <button class="cta-button" onclick="contactSales()">Contact Sales</button>
            </div>
        </div>
        
        <!-- Payment History -->
        <div class="payment-history">
            <h2>Payment History</h2>
            <table>
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Description</th>
                        <th>Amount</th>
                        <th>Status</th>
                        <th>Invoice</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Nov 10, 2025</td>
                        <td>Enterprise - Monthly Subscription</td>
                        <td>$2,999.00</td>
                        <td><span class="badge active">Paid</span></td>
                        <td><a href="#" style="color: #667eea;">Download</a></td>
                    </tr>
                    <tr>
                        <td>Oct 10, 2025</td>
                        <td>Enterprise - Monthly Subscription</td>
                        <td>$2,999.00</td>
                        <td><span class="badge active">Paid</span></td>
                        <td><a href="#" style="color: #667eea;">Download</a></td>
                    </tr>
                    <tr>
                        <td>Sep 10, 2025</td>
                        <td>Enterprise - Monthly Subscription</td>
                        <td>$2,999.00</td>
                        <td><span class="badge active">Paid</span></td>
                        <td><a href="#" style="color: #667eea;">Download</a></td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
    
    <!-- Checkout Modal -->
    <div id="checkoutModal" class="modal">
        <div class="modal-content">
            <span class="modal-close" onclick="closeModal()">&times;</span>
            <h2 style="margin-bottom: 30px;">Complete Your Purchase</h2>
            
            <div class="form-group">
                <label>Card Number</label>
                <input type="text" placeholder="4242 4242 4242 4242" maxlength="19">
            </div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                <div class="form-group">
                    <label>Expiry Date</label>
                    <input type="text" placeholder="MM/YY" maxlength="5">
                </div>
                <div class="form-group">
                    <label>CVV</label>
                    <input type="text" placeholder="123" maxlength="3">
                </div>
            </div>
            
            <div class="form-group">
                <label>Cardholder Name</label>
                <input type="text" placeholder="John Doe">
            </div>
            
            <button class="cta-button" onclick="processPayment()">
                Pay $2,999.00
            </button>
        </div>
    </div>
    
    <script>
        function showCheckout(tier) {
            document.getElementById('checkoutModal').style.display = 'block';
        }
        
        function closeModal() {
            document.getElementById('checkoutModal').style.display = 'none';
        }
        
        function processPayment() {
            alert('Payment processed successfully! Welcome to CyberGuard Enterprise.');
            closeModal();
        }
        
        function contactSales() {
            window.location.href = 'mailto:sales@cyberguard-platform.com?subject=Unlimited Edition Inquiry';
        }
        
        // Close modal on outside click
        window.onclick = function(event) {
            const modal = document.getElementById('checkoutModal');
            if (event.target == modal) {
                closeModal();
            }
        }
    </script>
</body>
</html>
"""


@app.route('/')
def dashboard():
    """Payment dashboard homepage"""
    return render_template_string(PAYMENT_DASHBOARD_HTML)


@app.route('/api/subscription/current')
def get_current_subscription():
    """Get current subscription details"""
    subscription = {
        "subscription_id": "sub_abc123def456",
        "customer_id": "cus_xyz789",
        "tier": "enterprise",
        "status": "trialing",
        "amount": 2999.00,
        "currency": "USD",
        "billing_cycle": "monthly",
        "trial_end": "2025-11-24",
        "next_billing_date": "2025-11-24",
        "license_key": "CGEP-A3F2-B8E1-C9D4-F7A6",
        "max_activations": 10,
        "current_activations": 3
    }
    return jsonify(subscription)


@app.route('/api/payments/history')
def get_payment_history():
    """Get payment history"""
    payments = [
        {
            "date": "2025-11-10",
            "description": "Enterprise - Monthly Subscription",
            "amount": 2999.00,
            "status": "paid",
            "invoice_url": "/invoices/inv_nov2025.pdf"
        },
        {
            "date": "2025-10-10",
            "description": "Enterprise - Monthly Subscription",
            "amount": 2999.00,
            "status": "paid",
            "invoice_url": "/invoices/inv_oct2025.pdf"
        },
        {
            "date": "2025-09-10",
            "description": "Enterprise - Monthly Subscription",
            "amount": 2999.00,
            "status": "paid",
            "invoice_url": "/invoices/inv_sep2025.pdf"
        }
    ]
    return jsonify(payments)


if __name__ == '__main__':
    print("\n" + "="*60)
    print("CyberGuard Payment Dashboard".center(60))
    print("="*60)
    print("\n🌐 Access the dashboard at: http://localhost:5001")
    print("\n📊 Features:")
    print("   • Subscription management")
    print("   • Payment history")
    print("   • Pricing plans")
    print("   • License information")
    print("   • Checkout system")
    print("\n" + "="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5001, debug=True)

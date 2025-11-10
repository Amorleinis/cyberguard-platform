#!/usr/bin/env python3
"""
CyberGuard Enterprise Platform - Website Server

Simple Flask server to run the marketing website locally.
Serves static HTML/CSS/JS files with live reload.

Usage:
    python website_server.py

Then open: http://localhost:8000
"""

from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
import os
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Get the website directory
WEBSITE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'website')

# Ensure website directory exists
os.makedirs(WEBSITE_DIR, exist_ok=True)
os.makedirs(os.path.join(WEBSITE_DIR, 'css'), exist_ok=True)
os.makedirs(os.path.join(WEBSITE_DIR, 'js'), exist_ok=True)
os.makedirs(os.path.join(WEBSITE_DIR, 'images'), exist_ok=True)

@app.route('/')
def index():
    """Serve the main index.html page"""
    return send_from_directory(WEBSITE_DIR, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files (CSS, JS, images, etc.)"""
    return send_from_directory(WEBSITE_DIR, path)

@app.route('/api/contact', methods=['POST'])
def contact_form():
    """Handle contact form submissions"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'message']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Log the contact submission (in production, save to database or send email)
        contact_data = {
            'name': data.get('name'),
            'email': data.get('email'),
            'company': data.get('company', 'Not provided'),
            'message': data.get('message'),
            'timestamp': datetime.now().isoformat(),
            'user_agent': request.headers.get('User-Agent'),
            'ip_address': request.remote_addr
        }
        
        print("\n" + "="*60)
        print("NEW CONTACT FORM SUBMISSION")
        print("="*60)
        print(f"Name:    {contact_data['name']}")
        print(f"Email:   {contact_data['email']}")
        print(f"Company: {contact_data['company']}")
        print(f"Message: {contact_data['message']}")
        print(f"Time:    {contact_data['timestamp']}")
        print("="*60 + "\n")
        
        # In production, you would:
        # 1. Save to database
        # 2. Send email notification to sales team
        # 3. Send confirmation email to customer
        # 4. Add to CRM system
        
        # For now, save to a JSON file
        contacts_file = os.path.join(os.path.dirname(__file__), 'contacts.json')
        contacts = []
        
        if os.path.exists(contacts_file):
            with open(contacts_file, 'r') as f:
                try:
                    contacts = json.load(f)
                except:
                    contacts = []
        
        contacts.append(contact_data)
        
        with open(contacts_file, 'w') as f:
            json.dump(contacts, f, indent=2)
        
        return jsonify({
            'success': True,
            'message': 'Thank you for contacting us! We will get back to you within 24 hours.'
        })
        
    except Exception as e:
        print(f"Error processing contact form: {e}")
        return jsonify({
            'success': False,
            'error': 'An error occurred processing your request. Please try again.'
        }), 500

@app.route('/api/newsletter', methods=['POST'])
def newsletter_signup():
    """Handle newsletter signup"""
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({
                'success': False,
                'error': 'Email is required'
            }), 400
        
        # Log newsletter signup
        print(f"\n📧 Newsletter signup: {email}")
        
        # In production, add to email marketing platform (Mailchimp, SendGrid, etc.)
        
        return jsonify({
            'success': True,
            'message': 'Successfully subscribed to newsletter!'
        })
        
    except Exception as e:
        print(f"Error processing newsletter signup: {e}")
        return jsonify({
            'success': False,
            'error': 'An error occurred. Please try again.'
        }), 500

@app.route('/api/demo-request', methods=['POST'])
def demo_request():
    """Handle demo requests"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'company']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        demo_data = {
            'name': data.get('name'),
            'email': data.get('email'),
            'company': data.get('company'),
            'phone': data.get('phone', 'Not provided'),
            'employees': data.get('employees', 'Not provided'),
            'timestamp': datetime.now().isoformat()
        }
        
        print("\n" + "="*60)
        print("NEW DEMO REQUEST")
        print("="*60)
        print(f"Name:      {demo_data['name']}")
        print(f"Email:     {demo_data['email']}")
        print(f"Company:   {demo_data['company']}")
        print(f"Phone:     {demo_data['phone']}")
        print(f"Employees: {demo_data['employees']}")
        print(f"Time:      {demo_data['timestamp']}")
        print("="*60 + "\n")
        
        # Save to file
        demos_file = os.path.join(os.path.dirname(__file__), 'demo_requests.json')
        demos = []
        
        if os.path.exists(demos_file):
            with open(demos_file, 'r') as f:
                try:
                    demos = json.load(f)
                except:
                    demos = []
        
        demos.append(demo_data)
        
        with open(demos_file, 'w') as f:
            json.dump(demos, f, indent=2)
        
        return jsonify({
            'success': True,
            'message': 'Demo request received! Our team will contact you within 24 hours.'
        })
        
    except Exception as e:
        print(f"Error processing demo request: {e}")
        return jsonify({
            'success': False,
            'error': 'An error occurred. Please try again.'
        }), 500

@app.route('/api/pricing', methods=['GET'])
def get_pricing():
    """Get current pricing information"""
    pricing = {
        'community': {
            'name': 'Community',
            'price': 0,
            'period': 'month',
            'features': [
                'Basic threat detection',
                'Core security features',
                'Community support',
                '1 user',
                '1,000 events/day'
            ]
        },
        'professional': {
            'name': 'Professional',
            'price': 499,
            'annual_price': 4990,
            'period': 'month',
            'features': [
                'ML-powered detection',
                'Advanced analytics',
                'Email support (24h response)',
                'Up to 10 users',
                '100,000 events/day',
                'API access'
            ]
        },
        'enterprise': {
            'name': 'Enterprise',
            'price': 2999,
            'annual_price': 29990,
            'period': 'month',
            'features': [
                'All Professional features',
                'SIEM integration',
                '24/7 support (1h response SLA)',
                'Unlimited users',
                'Unlimited events',
                'Custom integrations',
                'Dedicated account manager'
            ]
        },
        'unlimited': {
            'name': 'Unlimited',
            'price': 'Custom',
            'period': 'custom',
            'features': [
                'All Enterprise features',
                'On-premise deployment',
                'Custom development',
                'Training & certification',
                '99.99% SLA',
                'Dedicated support engineer',
                'White-label options'
            ]
        }
    }
    
    return jsonify(pricing)

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get platform statistics"""
    stats = {
        'threat_indicators': 113500,
        'detection_accuracy': 95,
        'threats_per_second': 1000,
        'cve_entries': 138728,
        'customers': 250,
        'countries': 42,
        'uptime': 99.99
    }
    
    return jsonify(stats)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'CyberGuard Website'
    })

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return send_from_directory(WEBSITE_DIR, 'index.html')

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🛡️  CYBERGUARD ENTERPRISE PLATFORM - WEBSITE SERVER")
    print("="*60)
    print("\nWebsite URL:  http://localhost:8000")
    print("API Docs:     http://localhost:8000/api/pricing")
    print("Health Check: http://localhost:8000/health")
    print("\nPress Ctrl+C to stop the server")
    print("="*60 + "\n")
    
    # Run the Flask server
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True,
        use_reloader=True
    )

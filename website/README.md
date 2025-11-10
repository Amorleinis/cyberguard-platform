# CyberGuard Enterprise Platform - Marketing Website

Professional marketing website for CyberGuard Enterprise Platform - ML-powered cybersecurity solution.

## 🌐 Live Demo

**Local Development:** http://localhost:8000

## ✨ Features

### Landing Page
- **Hero Section** - Compelling headline with platform statistics
- **Features Grid** - 8 key platform capabilities
- **Platform Stats** - ROI metrics and performance indicators
- **Pricing Cards** - 4 pricing tiers (Community, Professional, Enterprise, Unlimited)
- **Contact Form** - Lead capture with validation
- **Responsive Design** - Mobile, tablet, and desktop optimized

### Key Sections
1. **Navigation** - Sticky header with smooth scroll
2. **Trusted By** - Social proof from Fortune 500 companies
3. **Features** - ML detection, SIEM integration, real-time monitoring
4. **Stats Dashboard** - 87% reduction in incidents, $500K+ savings
5. **Pricing** - Monthly/Annual toggle with featured plan
6. **CTA Section** - Clear call-to-action for trials
7. **Contact** - Multi-channel contact information
8. **Footer** - Links, compliance badges, sitemap

### Technical Features
- **Smooth Animations** - Scroll-triggered animations
- **Interactive Pricing** - Monthly/Annual price toggle
- **Form Validation** - Real-time email validation
- **Mobile Menu** - Responsive hamburger menu
- **Threat Chart** - Animated data visualization
- **Counter Animation** - Number count-up effects
- **Parallax Effects** - Subtle scroll effects
- **SEO Optimized** - Meta tags, semantic HTML
- **Performance** - Lazy loading, optimized assets

## 🚀 Quick Start

### Run Locally

```bash
# Start the website server
python scripts/website_server.py
```

Open your browser to: **http://localhost:8000**

### Files Structure

```
website/
├── index.html          # Main landing page
├── css/
│   └── style.css      # Complete stylesheet
└── js/
    └── main.js        # JavaScript functionality
```

## 📊 API Endpoints

The website server includes REST API endpoints:

### Contact Form
```http
POST /api/contact
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@company.com",
  "company": "Acme Corp",
  "message": "Interested in Enterprise plan"
}
```

### Demo Request
```http
POST /api/demo-request
Content-Type: application/json

{
  "name": "Jane Smith",
  "email": "jane@company.com",
  "company": "Tech Inc",
  "phone": "+1-555-0100",
  "employees": "1000-5000"
}
```

### Newsletter Signup
```http
POST /api/newsletter
Content-Type: application/json

{
  "email": "subscriber@email.com"
}
```

### Get Pricing
```http
GET /api/pricing
```

Returns current pricing for all tiers.

### Get Stats
```http
GET /api/stats
```

Returns platform statistics (IOCs, accuracy, customers, etc.).

## 🎨 Design System

### Colors
- **Primary:** #0066ff (Blue)
- **Secondary:** #00d4ff (Cyan)
- **Success:** #00c853 (Green)
- **Warning:** #ffab00 (Orange)
- **Danger:** #ff3d00 (Red)
- **Dark:** #0a0e27 (Navy)

### Typography
- **Font Family:** Inter (Google Fonts)
- **Headings:** 700-800 weight
- **Body:** 400 weight

### Spacing
- Uses consistent spacing scale (0.5rem to 5rem)
- Mobile-first responsive breakpoints

## 📱 Responsive Breakpoints

- **Desktop:** 1024px+
- **Tablet:** 768px - 1023px
- **Mobile:** < 768px

## 🔧 Customization

### Update Pricing

Edit the pricing tiers in `index.html`:

```html
<div class="pricing-card">
    <h3 class="pricing-tier">Professional</h3>
    <div class="pricing-price">
        <span class="price-amount" data-monthly="499" data-annual="4990">$499</span>
        <span class="price-period">/month</span>
    </div>
    <!-- Features list -->
</div>
```

### Update Contact Info

Edit contact information in the Contact section:

```html
<div class="contact-item">
    <div class="contact-icon">📧</div>
    <div>
        <div class="contact-label">Email</div>
        <a href="mailto:sales@cyberguard-platform.com">sales@cyberguard-platform.com</a>
    </div>
</div>
```

### Update Stats

Edit hero stats in `index.html`:

```html
<div class="stat">
    <div class="stat-number">113,500+</div>
    <div class="stat-label">Threat Indicators</div>
</div>
```

## 🎯 SEO Optimization

The website includes:
- **Meta Description:** Cybersecurity platform description
- **Meta Keywords:** Relevant industry keywords
- **Semantic HTML:** Proper heading hierarchy
- **Alt Text:** Image descriptions (when images added)
- **Open Graph Tags:** Social media sharing (add to `<head>`)

### Add Open Graph Tags

```html
<meta property="og:title" content="CyberGuard Enterprise Platform">
<meta property="og:description" content="ML-powered cybersecurity threat detection">
<meta property="og:image" content="/images/og-image.png">
<meta property="og:url" content="https://cyberguard-platform.com">
```

## 📈 Analytics Integration

Add Google Analytics to track visitors:

```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

## 🚀 Production Deployment

### Option 1: Static Hosting (Netlify, Vercel)

1. Push to GitHub repository
2. Connect to Netlify/Vercel
3. Deploy `website/` directory
4. Configure custom domain

### Option 2: AWS S3 + CloudFront

```bash
# Build and deploy to S3
aws s3 sync website/ s3://your-bucket-name --delete
aws cloudfront create-invalidation --distribution-id YOUR_DIST_ID --paths "/*"
```

### Option 3: Docker Container

```dockerfile
FROM nginx:alpine
COPY website/ /usr/share/nginx/html/
EXPOSE 80
```

Build and run:
```bash
docker build -t cyberguard-website .
docker run -p 80:80 cyberguard-website
```

### Option 4: Flask Production Server

Use the included `website_server.py` with Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 scripts.website_server:app
```

## 📧 Email Integration

### SendGrid Setup

```python
# In website_server.py contact_form endpoint
import sendgrid
from sendgrid.helpers.mail import Mail

sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
message = Mail(
    from_email='noreply@cyberguard-platform.com',
    to_emails='sales@cyberguard-platform.com',
    subject='New Contact Form Submission',
    html_content=f'<strong>Name:</strong> {name}<br>...'
)
response = sg.send(message)
```

## 🎨 Adding Images

Add company logos and screenshots:

```
website/images/
├── logo.png           # Main logo
├── hero-dashboard.png # Dashboard screenshot
├── features/          # Feature illustrations
├── customers/         # Customer logos
└── og-image.png       # Social media preview
```

Update image paths in HTML:
```html
<img src="images/hero-dashboard.png" alt="CyberGuard Dashboard">
```

## 🔒 Security Best Practices

1. **HTTPS Only** - Always use SSL in production
2. **CORS** - Restrict API origins
3. **Rate Limiting** - Prevent form spam
4. **Input Validation** - Sanitize all user input
5. **CSP Headers** - Content Security Policy

### Add CSP Header

```python
@app.after_request
def set_csp(response):
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' fonts.googleapis.com; font-src fonts.gstatic.com;"
    return response
```

## 📊 Performance Optimization

Current optimizations:
- ✅ Lazy loading for images
- ✅ Minified CSS/JS (for production)
- ✅ Intersection Observer for animations
- ✅ Efficient DOM manipulation
- ✅ CSS Grid for layouts
- ✅ Web fonts optimized

### Add Minification

```bash
# Install minifiers
npm install -g clean-css-cli uglify-js html-minifier

# Minify files
cleancss website/css/style.css -o website/css/style.min.css
uglifyjs website/js/main.js -o website/js/main.min.js
html-minifier website/index.html -o website/index.min.html --collapse-whitespace --remove-comments
```

## 🎉 Easter Eggs

The website includes a Konami Code easter egg:

**Try it:** ↑ ↑ ↓ ↓ ← → ← → B A

Reveals a special discount code!

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Support

- **Email:** support@cyberguard-platform.com
- **Sales:** sales@cyberguard-platform.com
- **Emergency:** +1 (555) CYBER-911
- **Documentation:** https://docs.cyberguard-platform.com

## 🎯 Conversion Optimization

### A/B Testing Ideas

1. **Hero CTA** - "Start Free Trial" vs "Get Started"
2. **Pricing Toggle** - Default Monthly vs Annual
3. **Form Length** - Short form vs detailed form
4. **Social Proof** - Customer logos vs testimonials

### Analytics Events to Track

- Button clicks (CTA, pricing, demo)
- Form submissions
- Pricing card interactions
- Scroll depth
- Time on page
- Exit pages

## 🚀 Next Steps

1. **Add Real Content**
   - Customer testimonials
   - Case studies
   - Blog posts
   - Product screenshots

2. **Integrate CRM**
   - HubSpot
   - Salesforce
   - Pipedrive

3. **Live Chat**
   - Intercom
   - Drift
   - Zendesk

4. **Marketing Automation**
   - Email sequences
   - Drip campaigns
   - Lead scoring

---

**Built with ❤️ by CyberGuard Industries**

For development questions, contact: dev@cyberguard-platform.com

# Advanced Analytics & Reporting

## Overview

The Advanced Analytics Engine provides comprehensive threat analysis, risk assessment, and automated report generation. It transforms raw security data into actionable intelligence with beautiful visualizations and executive-ready reports.

## Features

### 1. Threat Trend Analysis
- **Time Windows**: Configurable analysis periods (7, 30, 90 days)
- **Daily Statistics**: Threat counts, severity distribution, type analysis
- **Trend Detection**: Increasing, decreasing, or stable patterns
- **Peak Analysis**: Identifies highest threat activity periods
- **Change Percentage**: Quantifies threat evolution

### 2. Risk Score Calculation
- **Multi-Component**: 5-factor risk assessment
  - **Threat Volume** (25 points): Number of active threats
  - **Threat Severity** (30 points): Critical/High severity weighting
  - **Attack Diversity** (20 points): Variety of attack types
  - **Response Effectiveness** (15 points): Success rate of mitigations
  - **Trend Factor** (10 points): Direction of threat evolution
- **Scale**: 0-100 risk score
- **Risk Levels**: LOW (<25), MEDIUM (25-50), HIGH (50-75), CRITICAL (75+)
- **Recommendations**: Automated action items per risk level

### 3. Attack Pattern Identification
- **Time Patterns**: Peak hours, peak days, time clustering
- **Sequential Attacks**: Detects attack chains within time windows
- **Target Analysis**: Identifies commonly targeted resources
- **Correlation**: Finds co-occurring threats

### 4. HTML Report Generation
- **Beautiful Design**: CSS-styled professional reports
- **Sections**:
  - Executive Summary
  - Threat Statistics
  - Risk Assessment
  - Top Threats Table
  - Attack Patterns
  - Recommendations
- **Time-stamped**: Automatic generation timestamps
- **Responsive**: Mobile-friendly layouts

### 5. PDF Report Generation
- **Professional Layout**: ReportLab-powered PDF generation
- **Tables**: Formatted threat data tables
- **Charts**: Visual risk indicators
- **Branding**: Customizable headers/footers
- **Print-Ready**: Optimized for printing

## Installation

### Required Dependencies
```bash
pip install reportlab  # For PDF generation
```

### Optional Dependencies
```bash
pip install matplotlib  # For advanced charts
pip install plotly      # For interactive visualizations
```

## Usage

### Analyze Threat Trends

```python
from scripts.advanced_analytics import AdvancedAnalyticsEngine

# Initialize engine
analytics = AdvancedAnalyticsEngine('.')

# Load threat history
threats = [
    {'timestamp': '2025-11-10T10:00:00', 'severity': 'HIGH', 'threat_type': 'malware'},
    {'timestamp': '2025-11-09T15:30:00', 'severity': 'MEDIUM', 'threat_type': 'phishing'},
    # ... more threats
]

# Analyze trends
trends = analytics.analyze_threat_trends(threats, time_window_days=7)
print(f"Total threats: {trends['summary']['total_threats']}")
print(f"Daily average: {trends['summary']['daily_average']:.1f}")
print(f"Trend: {trends['summary']['trend_direction']}")
```

### Calculate Risk Score

```python
current_threats = [...]  # Recent threats
historical_context = {
    'daily_average': 50,
    'peak_threats': 200
}

risk = analytics.calculate_risk_score(current_threats, historical_context)
print(f"Risk Score: {risk['total_score']}/100")
print(f"Risk Level: {risk['risk_level']}")
print(f"Top Risk Component: {max(risk['components'].items(), key=lambda x: x[1])}")

# Get recommendations
for rec in risk['recommendation']:
    print(f"  - {rec}")
```

### Identify Attack Patterns

```python
patterns = analytics.identify_attack_patterns(threats)

# Time patterns
time_patterns = patterns['time_patterns']
print(f"Peak hours: {time_patterns['peak_hours']}")
print(f"Peak days: {time_patterns['peak_days']}")

# Sequential attacks
sequences = patterns['sequential_attacks']
for seq in sequences[:5]:
    print(f"Attack chain: {seq['sequence']}")
    print(f"  Duration: {seq['duration_minutes']} minutes")

# Target analysis
targets = patterns['target_patterns']
print(f"Most targeted ports: {targets['common_ports'][:5]}")
```

### Generate HTML Report

```python
# Generate comprehensive HTML report
report_path = analytics.generate_html_report(
    threat_data=threats,
    risk_assessment=risk,
    filename='security_report_2025_11_10.html'
)

print(f"Report generated: {report_path}")
# Opens in browser automatically
```

### Generate PDF Report

```python
# Generate executive PDF report
pdf_path = analytics.generate_pdf_report(
    threat_data=threats,
    risk_assessment=risk,
    trends_summary=trends['summary'],
    filename='executive_report_2025_11_10.pdf'
)

print(f"PDF report generated: {pdf_path}")
```

## Report Customization

### Custom HTML Template

Create `data/config/report_template.html`:
```html
<!DOCTYPE html>
<html>
<head>
    <title>{{title}}</title>
    <style>
        /* Your custom CSS */
    </style>
</head>
<body>
    <h1>{{company_name}} Security Report</h1>
    {{content}}
</body>
</html>
```

### PDF Styling

```python
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

styles = getSampleStyleSheet()
custom_style = styles['Normal'].clone('CustomStyle')
custom_style.textColor = colors.HexColor('#667eea')
custom_style.fontSize = 12

# Use in report generation
analytics.pdf_style = custom_style
```

## Scheduled Reporting

### Daily Reports
```python
from datetime import datetime, timedelta
import schedule

def daily_report():
    yesterday = datetime.now() - timedelta(days=1)
    threats = get_threats_for_date(yesterday)
    
    report = analytics.generate_html_report(threats)
    send_email_report(report)  # Your email function

schedule.every().day.at("08:00").do(daily_report)
```

### Weekly Executive Summary
```python
def weekly_summary():
    week_threats = get_threats_for_week()
    trends = analytics.analyze_threat_trends(week_threats, 7)
    risk = analytics.calculate_risk_score(week_threats, historical_data)
    
    pdf = analytics.generate_pdf_report(
        week_threats, risk, trends['summary'],
        filename=f'weekly_executive_{datetime.now():%Y%m%d}.pdf'
    )
    
    send_to_executives(pdf)

schedule.every().monday.at("09:00").do(weekly_summary)
```

## Performance Metrics

### Report Generation Speed
- **HTML**: 50-100 threats in <1 second
- **PDF**: 50-100 threats in 2-3 seconds
- **Large Reports**: 1000+ threats in <10 seconds

### Analytics Processing
- **Trend Analysis**: <500ms for 1000 threats
- **Risk Calculation**: <100ms
- **Pattern Discovery**: 1-2 seconds for 1000 threats

## Integration Examples

### With ML Detection
```python
from scripts.ml_threat_detection import MLThreatDetectionEngine

ml_engine = MLThreatDetectionEngine('.')
analytics = AdvancedAnalyticsEngine('.')

# Enrich threats with ML confidence
for threat in threats:
    ml_result = ml_engine.classify_threat(threat)
    threat['ml_confidence'] = ml_result['confidence']
    threat['ml_category'] = ml_result['category']

# Generate ML-enhanced report
report = analytics.generate_html_report(threats)
```

### With SIEM Integration
```python
from scripts.siem_integration import SIEMIntegrationHub

siem = SIEMIntegrationHub('.')

# Query SIEM for threat data
siem_threats = siem.query_siem('splunk', {
    'query': 'index=security severity=HIGH',
    'time_range': '7d'
})

# Analyze SIEM data
trends = analytics.analyze_threat_trends(siem_threats)
```

### With Dashboard
```python
from scripts.threat_dashboard import create_dashboard_app

app = create_dashboard_app('.')

@app.route('/analytics/risk')
def get_risk_score():
    threats = get_recent_threats()
    risk = analytics.calculate_risk_score(threats, get_historical_context())
    return jsonify(risk)

@app.route('/analytics/report/<report_type>')
def generate_report(report_type):
    threats = get_recent_threats()
    if report_type == 'html':
        return send_file(analytics.generate_html_report(threats))
    elif report_type == 'pdf':
        return send_file(analytics.generate_pdf_report(threats))
```

## Configuration

Create `data/config/analytics_config.json`:
```json
{
    "risk_scoring": {
        "weights": {
            "threat_volume": 25,
            "threat_severity": 30,
            "attack_diversity": 20,
            "response_effectiveness": 15,
            "trend_factor": 10
        },
        "thresholds": {
            "low": 25,
            "medium": 50,
            "high": 75
        }
    },
    "patterns": {
        "sequence_window_minutes": 60,
        "correlation_window_minutes": 10,
        "min_pattern_size": 3
    },
    "reports": {
        "default_time_window": 7,
        "company_name": "Your Organization",
        "logo_path": "data/assets/logo.png",
        "theme_color": "#667eea"
    }
}
```

## Best Practices

1. **Regular Analysis**: Run trend analysis weekly
2. **Baseline Establishment**: Build 30-day historical baseline
3. **Threshold Tuning**: Adjust risk thresholds to your environment
4. **Report Distribution**: Automate report delivery to stakeholders
5. **Pattern Review**: Manually review discovered patterns monthly

## Troubleshooting

### Issue: Reports Not Generating
**Solution**: Check write permissions in `data/reports/` directory

### Issue: PDF Generation Fails
**Solution**: Ensure ReportLab is installed: `pip install reportlab`

### Issue: Inaccurate Risk Scores
**Solution**: Verify historical context data is representative

## Advanced Features

### Custom Risk Components
```python
def custom_risk_calculation(threats):
    custom_score = 0
    
    # Add your custom logic
    if has_ransomware(threats):
        custom_score += 40
    
    if targeting_critical_systems(threats):
        custom_score += 30
    
    return min(custom_score, 100)
```

### Multi-Tenant Reporting
```python
def generate_tenant_reports(tenant_id):
    threats = get_threats_by_tenant(tenant_id)
    
    report = analytics.generate_html_report(
        threats,
        filename=f'report_{tenant_id}_{datetime.now():%Y%m%d}.html'
    )
    
    return report
```

## API Reference

See inline documentation in `scripts/advanced_analytics.py` for detailed API reference.

## Resources

- [ReportLab Documentation](https://www.reportlab.com/docs/)
- [Security Metrics Guide](https://www.sans.org/reading-room/whitepapers/metrics/)
- [Risk Scoring Frameworks](https://www.nist.gov/cyberframework)

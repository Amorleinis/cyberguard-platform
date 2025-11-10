"""
Advanced Analytics & Reporting System
PDF/HTML report generation, trend analysis, attack pattern recognition
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict, Counter
import io

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib import colors
    reportlab_available = True
except ImportError:
    reportlab_available = False
    print("⚠️  ReportLab not installed. PDF generation will be disabled.")


class AdvancedAnalyticsEngine:
    """Advanced threat analytics and comprehensive reporting"""
    
    def __init__(self, workspace_root):
        self.workspace_root = Path(workspace_root)
        self.reports_dir = self.workspace_root / 'data' / 'reports'
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Analytics cache
        self.analytics_cache = {
            'threat_trends': {},
            'attack_patterns': {},
            'risk_scores': {},
            'top_threats': []
        }
        
        print("📊 Advanced Analytics Engine initialized")
        print(f"   ReportLab: {'✅' if reportlab_available else '❌ (PDF disabled)'}")
        print(f"   Reports directory: {self.reports_dir}")
    
    
    def analyze_threat_trends(self, threat_history, time_window_days=30):
        """Analyze threat trends over time"""
        if not threat_history:
            return {'trends': [], 'summary': 'No data available'}
        
        # Group threats by day
        threats_by_day = defaultdict(list)
        cutoff_date = datetime.now() - timedelta(days=time_window_days)
        
        for threat in threat_history:
            try:
                timestamp = datetime.fromisoformat(threat.get('timestamp', ''))
                if timestamp >= cutoff_date:
                    day = timestamp.date().isoformat()
                    threats_by_day[day].append(threat)
            except:
                continue
        
        # Calculate daily statistics
        trends = []
        for day in sorted(threats_by_day.keys()):
            day_threats = threats_by_day[day]
            
            severity_counts = Counter(t.get('severity', 'UNKNOWN') for t in day_threats)
            type_counts = Counter(t.get('threat_type', 'unknown') for t in day_threats)
            
            trends.append({
                'date': day,
                'total_threats': len(day_threats),
                'critical': severity_counts.get('CRITICAL', 0),
                'high': severity_counts.get('HIGH', 0),
                'medium': severity_counts.get('MEDIUM', 0),
                'low': severity_counts.get('LOW', 0),
                'top_type': type_counts.most_common(1)[0][0] if type_counts else 'none',
                'unique_types': len(type_counts)
            })
        
        # Calculate trend direction
        if len(trends) >= 2:
            recent_avg = sum(t['total_threats'] for t in trends[-7:]) / min(7, len(trends[-7:]))
            older_avg = sum(t['total_threats'] for t in trends[:7]) / min(7, len(trends[:7]))
            
            if recent_avg > older_avg * 1.2:
                trend_direction = 'increasing'
            elif recent_avg < older_avg * 0.8:
                trend_direction = 'decreasing'
            else:
                trend_direction = 'stable'
        else:
            trend_direction = 'insufficient_data'
        
        summary = {
            'period_days': time_window_days,
            'total_threats': sum(t['total_threats'] for t in trends),
            'daily_average': sum(t['total_threats'] for t in trends) / max(len(trends), 1),
            'peak_day': max(trends, key=lambda x: x['total_threats']) if trends else None,
            'trend_direction': trend_direction,
            'critical_count': sum(t['critical'] for t in trends),
            'high_count': sum(t['high'] for t in trends)
        }
        
        self.analytics_cache['threat_trends'] = {
            'trends': trends,
            'summary': summary,
            'generated': datetime.now().isoformat()
        }
        
        return {'trends': trends, 'summary': summary}
    
    
    def calculate_risk_score(self, current_threats, historical_context):
        """Calculate comprehensive risk score"""
        risk_components = {
            'threat_volume': 0,
            'threat_severity': 0,
            'attack_diversity': 0,
            'response_effectiveness': 0,
            'trend_factor': 0
        }
        
        # Threat volume component (0-20 points)
        threat_count = len(current_threats)
        risk_components['threat_volume'] = min(threat_count / 5, 20)
        
        # Threat severity component (0-30 points)
        severity_weights = {'CRITICAL': 10, 'HIGH': 7, 'MEDIUM': 4, 'LOW': 1}
        severity_score = sum(severity_weights.get(t.get('severity', 'LOW'), 1) for t in current_threats)
        risk_components['threat_severity'] = min(severity_score / 10, 30)
        
        # Attack diversity component (0-20 points)
        unique_types = len(set(t.get('threat_type', 'unknown') for t in current_threats))
        risk_components['attack_diversity'] = min(unique_types * 2, 20)
        
        # Response effectiveness component (0-15 points, inverted)
        blocked_count = sum(1 for t in current_threats if t.get('action') in ['BLOCKED', 'TERMINATED'])
        if current_threats:
            block_rate = blocked_count / len(current_threats)
            risk_components['response_effectiveness'] = 15 * (1 - block_rate)
        
        # Trend factor (0-15 points)
        if historical_context:
            recent_avg = len(current_threats)
            historical_avg = historical_context.get('daily_average', recent_avg)
            if historical_avg > 0:
                trend_ratio = recent_avg / historical_avg
                risk_components['trend_factor'] = min(trend_ratio * 7.5, 15)
        
        # Calculate total risk score (0-100)
        total_risk = sum(risk_components.values())
        
        # Determine risk level
        if total_risk >= 75:
            risk_level = 'CRITICAL'
        elif total_risk >= 50:
            risk_level = 'HIGH'
        elif total_risk >= 25:
            risk_level = 'MEDIUM'
        else:
            risk_level = 'LOW'
        
        result = {
            'total_score': round(total_risk, 2),
            'risk_level': risk_level,
            'components': risk_components,
            'calculated_at': datetime.now().isoformat(),
            'recommendation': self._get_risk_recommendation(risk_level)
        }
        
        self.analytics_cache['risk_scores'][datetime.now().date().isoformat()] = result
        
        return result
    
    
    def _get_risk_recommendation(self, risk_level):
        """Get recommendations based on risk level"""
        recommendations = {
            'CRITICAL': [
                'Activate incident response team',
                'Enable maximum security protocols',
                'Conduct emergency security review',
                'Consider network isolation for critical systems'
            ],
            'HIGH': [
                'Increase monitoring frequency',
                'Review and update firewall rules',
                'Conduct security audit',
                'Brief security team on current threats'
            ],
            'MEDIUM': [
                'Maintain enhanced vigilance',
                'Update threat signatures',
                'Review security logs daily',
                'Test backup and recovery procedures'
            ],
            'LOW': [
                'Continue standard monitoring',
                'Regular security updates',
                'Maintain current security posture'
            ]
        }
        
        return recommendations.get(risk_level, recommendations['LOW'])
    
    
    def identify_attack_patterns(self, threat_history):
        """Identify common attack patterns and sequences"""
        patterns = {
            'time_based': self._analyze_time_patterns(threat_history),
            'type_sequences': self._analyze_attack_sequences(threat_history),
            'target_patterns': self._analyze_target_patterns(threat_history),
            'correlation': self._analyze_threat_correlation(threat_history)
        }
        
        self.analytics_cache['attack_patterns'] = patterns
        
        return patterns
    
    
    def _analyze_time_patterns(self, threats):
        """Analyze when attacks occur"""
        hour_distribution = defaultdict(int)
        day_distribution = defaultdict(int)
        
        for threat in threats:
            try:
                timestamp = datetime.fromisoformat(threat.get('timestamp', ''))
                hour_distribution[timestamp.hour] += 1
                day_distribution[timestamp.strftime('%A')] += 1
            except:
                continue
        
        peak_hour = max(hour_distribution.items(), key=lambda x: x[1])[0] if hour_distribution else 0
        peak_day = max(day_distribution.items(), key=lambda x: x[1])[0] if day_distribution else 'Unknown'
        
        return {
            'peak_hour': peak_hour,
            'peak_day': peak_day,
            'hour_distribution': dict(hour_distribution),
            'day_distribution': dict(day_distribution)
        }
    
    
    def _analyze_attack_sequences(self, threats):
        """Identify common attack sequences"""
        # Sort threats by time
        sorted_threats = sorted(threats, key=lambda x: x.get('timestamp', ''))
        
        # Look for sequences (within 1 hour)
        sequences = []
        i = 0
        
        while i < len(sorted_threats) - 1:
            sequence = [sorted_threats[i]['threat_type']]
            j = i + 1
            
            while j < len(sorted_threats):
                try:
                    t1 = datetime.fromisoformat(sorted_threats[i]['timestamp'])
                    t2 = datetime.fromisoformat(sorted_threats[j]['timestamp'])
                    
                    if (t2 - t1).total_seconds() <= 3600:  # Within 1 hour
                        sequence.append(sorted_threats[j]['threat_type'])
                        j += 1
                    else:
                        break
                except:
                    break
            
            if len(sequence) >= 2:
                sequences.append(sequence)
            
            i = j if j > i + 1 else i + 1
        
        # Find common sequences
        sequence_counts = Counter(tuple(seq) for seq in sequences if len(seq) >= 2)
        
        return {
            'total_sequences': len(sequences),
            'common_sequences': [
                {'sequence': list(seq), 'count': count}
                for seq, count in sequence_counts.most_common(5)
            ]
        }
    
    
    def _analyze_target_patterns(self, threats):
        """Analyze what attackers are targeting"""
        targets = defaultdict(int)
        
        for threat in threats:
            indicator = threat.get('indicator', 'unknown')
            # Categorize targets
            if ':' in indicator or 'port' in indicator.lower():
                targets['network_ports'] += 1
            elif 'process' in threat.get('threat_type', '').lower():
                targets['processes'] += 1
            elif 'file' in threat.get('threat_type', '').lower():
                targets['files'] += 1
            elif 'domain' in threat.get('threat_type', '').lower():
                targets['dns'] += 1
            else:
                targets['other'] += 1
        
        return dict(targets)
    
    
    def _analyze_threat_correlation(self, threats):
        """Analyze correlations between different threat types"""
        # Simple correlation: which threats occur together
        correlations = []
        
        threat_types = list(set(t.get('threat_type', 'unknown') for t in threats))
        
        for i, type1 in enumerate(threat_types):
            for type2 in threat_types[i+1:]:
                # Count co-occurrences within 10 minutes
                co_occurrence = 0
                
                type1_threats = [t for t in threats if t.get('threat_type') == type1]
                type2_threats = [t for t in threats if t.get('threat_type') == type2]
                
                for t1 in type1_threats:
                    for t2 in type2_threats:
                        try:
                            ts1 = datetime.fromisoformat(t1.get('timestamp', ''))
                            ts2 = datetime.fromisoformat(t2.get('timestamp', ''))
                            
                            if abs((ts2 - ts1).total_seconds()) <= 600:  # 10 minutes
                                co_occurrence += 1
                        except:
                            continue
                
                if co_occurrence > 0:
                    correlations.append({
                        'types': [type1, type2],
                        'co_occurrences': co_occurrence,
                        'correlation_strength': co_occurrence / max(len(type1_threats), len(type2_threats))
                    })
        
        # Sort by correlation strength
        correlations.sort(key=lambda x: x['correlation_strength'], reverse=True)
        
        return correlations[:10]  # Top 10 correlations
    
    
    def generate_html_report(self, report_data):
        """Generate HTML threat report"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>CyberGuard Threat Intelligence Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                   color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; }}
        .section {{ background: white; padding: 20px; margin-bottom: 20px; 
                    border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .metric {{ display: inline-block; margin: 10px 20px; }}
        .metric-value {{ font-size: 2em; font-weight: bold; color: #667eea; }}
        .metric-label {{ color: #666; font-size: 0.9em; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #667eea; color: white; }}
        .risk-critical {{ color: #dc3545; font-weight: bold; }}
        .risk-high {{ color: #fd7e14; font-weight: bold; }}
        .risk-medium {{ color: #ffc107; font-weight: bold; }}
        .risk-low {{ color: #28a745; font-weight: bold; }}
        .footer {{ text-align: center; color: #666; margin-top: 40px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🛡️ CyberGuard Industries</h1>
        <h2>Threat Intelligence Report</h2>
        <p>Generated: {timestamp}</p>
    </div>
    
    <div class="section">
        <h2>Executive Summary</h2>
        <div class="metric">
            <div class="metric-value">{report_data.get('total_threats', 0)}</div>
            <div class="metric-label">Total Threats</div>
        </div>
        <div class="metric">
            <div class="metric-value">{report_data.get('critical_threats', 0)}</div>
            <div class="metric-label">Critical Threats</div>
        </div>
        <div class="metric">
            <div class="metric-value">{report_data.get('threats_blocked', 0)}</div>
            <div class="metric-label">Threats Blocked</div>
        </div>
        <div class="metric">
            <div class="metric-value risk-{report_data.get('risk_level', 'low').lower()}">
                {report_data.get('risk_score', 0)}/100
            </div>
            <div class="metric-label">Risk Score</div>
        </div>
    </div>
    
    <div class="section">
        <h2>Threat Breakdown</h2>
        <table>
            <tr>
                <th>Threat Type</th>
                <th>Count</th>
                <th>Severity</th>
                <th>Status</th>
            </tr>
"""
        
        for threat_summary in report_data.get('threat_breakdown', []):
            html += f"""
            <tr>
                <td>{threat_summary.get('type', 'Unknown')}</td>
                <td>{threat_summary.get('count', 0)}</td>
                <td class="risk-{threat_summary.get('severity', 'low').lower()}">
                    {threat_summary.get('severity', 'LOW')}
                </td>
                <td>{threat_summary.get('status', 'N/A')}</td>
            </tr>
"""
        
        html += """
        </table>
    </div>
    
    <div class="section">
        <h2>Recommendations</h2>
        <ul>
"""
        
        for recommendation in report_data.get('recommendations', []):
            html += f"            <li>{recommendation}</li>\n"
        
        html += """
        </ul>
    </div>
    
    <div class="footer">
        <p>CyberGuard Industries - Enterprise Cybersecurity Platform</p>
        <p>Confidential - For Internal Use Only</p>
    </div>
</body>
</html>
"""
        
        # Save report
        report_file = self.reports_dir / f"threat_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"   ✅ HTML report saved: {report_file}")
        return str(report_file)
    
    
    def generate_pdf_report(self, report_data):
        """Generate PDF threat report"""
        if not reportlab_available:
            print("   ⚠️  ReportLab not installed. Use HTML report instead.")
            return None
        
        report_file = self.reports_dir / f"threat_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        doc = SimpleDocTemplate(str(report_file), pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=30
        )
        
        story.append(Paragraph("🛡️ CyberGuard Industries", title_style))
        story.append(Paragraph("Threat Intelligence Report", styles['Heading2']))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        story.append(Spacer(1, 0.5*inch))
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", styles['Heading2']))
        summary_data = [
            ['Metric', 'Value'],
            ['Total Threats', str(report_data.get('total_threats', 0))],
            ['Critical Threats', str(report_data.get('critical_threats', 0))],
            ['Threats Blocked', str(report_data.get('threats_blocked', 0))],
            ['Risk Score', f"{report_data.get('risk_score', 0)}/100"],
            ['Risk Level', report_data.get('risk_level', 'LOW')]
        ]
        
        summary_table = Table(summary_data)
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Recommendations
        story.append(Paragraph("Recommendations", styles['Heading2']))
        for i, rec in enumerate(report_data.get('recommendations', []), 1):
            story.append(Paragraph(f"{i}. {rec}", styles['Normal']))
            story.append(Spacer(1, 0.1*inch))
        
        # Build PDF
        doc.build(story)
        
        print(f"   ✅ PDF report saved: {report_file}")
        return str(report_file)
    
    
    def export_analytics_data(self, format='json'):
        """Export all analytics data"""
        export_data = {
            'generated_at': datetime.now().isoformat(),
            'analytics_cache': self.analytics_cache,
            'format_version': '1.0'
        }
        
        if format == 'json':
            export_file = self.reports_dir / f"analytics_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(export_file, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            print(f"   ✅ Analytics exported: {export_file}")
            return str(export_file)
        
        return None


if __name__ == '__main__':
    import sys
    from pathlib import Path
    
    workspace = Path(__file__).parent.parent
    
    print("=" * 70)
    print("📊 ADVANCED ANALYTICS ENGINE - DEMO")
    print("=" * 70)
    print()
    
    analytics = AdvancedAnalyticsEngine(workspace)
    
    # Create sample threat data
    sample_threats = []
    for i in range(50):
        threat = {
            'timestamp': (datetime.now() - timedelta(days=i % 10, hours=i % 24)).isoformat(),
            'threat_type': ['malware', 'phishing', 'ddos', 'malware'][i % 4],
            'severity': ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'][(i % 4)],
            'indicator': f'threat_{i}',
            'action': 'BLOCKED' if i % 3 == 0 else 'LOGGED'
        }
        sample_threats.append(threat)
    
    # Test threat trends
    print("\n📈 Analyzing Threat Trends...")
    trends = analytics.analyze_threat_trends(sample_threats, time_window_days=30)
    print(f"   Total threats: {trends['summary']['total_threats']}")
    print(f"   Daily average: {trends['summary']['daily_average']:.1f}")
    print(f"   Trend direction: {trends['summary']['trend_direction']}")
    
    # Test risk score calculation
    print("\n🎯 Calculating Risk Score...")
    risk = analytics.calculate_risk_score(sample_threats[:10], trends['summary'])
    print(f"   Risk Score: {risk['total_score']}/100")
    print(f"   Risk Level: {risk['risk_level']}")
    print(f"   Recommendations: {len(risk['recommendation'])} items")
    
    # Test attack pattern identification
    print("\n🔬 Identifying Attack Patterns...")
    patterns = analytics.identify_attack_patterns(sample_threats)
    print(f"   Peak hour: {patterns['time_based']['peak_hour']}:00")
    print(f"   Peak day: {patterns['time_based']['peak_day']}")
    print(f"   Common sequences: {len(patterns['type_sequences']['common_sequences'])}")
    print(f"   Correlations found: {len(patterns['correlation'])}")
    
    # Generate reports
    print("\n📄 Generating Reports...")
    report_data = {
        'total_threats': len(sample_threats),
        'critical_threats': sum(1 for t in sample_threats if t['severity'] == 'CRITICAL'),
        'threats_blocked': sum(1 for t in sample_threats if t['action'] == 'BLOCKED'),
        'risk_score': risk['total_score'],
        'risk_level': risk['risk_level'],
        'threat_breakdown': [
            {'type': 'Malware', 'count': 13, 'severity': 'HIGH', 'status': 'Blocked'},
            {'type': 'Phishing', 'count': 12, 'severity': 'MEDIUM', 'status': 'Monitored'}
        ],
        'recommendations': risk['recommendation']
    }
    
    html_report = analytics.generate_html_report(report_data)
    print(f"   HTML: {html_report}")
    
    if reportlab_available:
        pdf_report = analytics.generate_pdf_report(report_data)
        print(f"   PDF: {pdf_report}")
    
    # Export analytics
    print("\n💾 Exporting Analytics...")
    export_file = analytics.export_analytics_data()
    print(f"   Exported to: {export_file}")
    
    print("\n✅ Analytics Demo complete!")

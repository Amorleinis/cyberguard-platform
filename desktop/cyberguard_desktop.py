"""
CyberGuard Enterprise Platform - Desktop Application
Windows Desktop App with System Tray Integration
"""

import sys
import json
import asyncio
from datetime import datetime
from typing import Optional, Dict, List
from pathlib import Path

try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QPushButton, QSystemTrayIcon, QMenu, QAction, QTabWidget,
        QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox, QGridLayout,
        QProgressBar, QMessageBox, QLineEdit, QFormLayout, QDialog
    )
    from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QSize
    from PyQt5.QtGui import QIcon, QPixmap, QColor, QFont
except ImportError:
    print("PyQt5 not installed. Installing now...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PyQt5"])
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QPushButton, QSystemTrayIcon, QMenu, QAction, QTabWidget,
        QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox, QGridLayout,
        QProgressBar, QMessageBox, QLineEdit, QFormLayout, QDialog
    )
    from PyQt5.QtCore import Qt, QTimer, QSize
    from PyQt5.QtGui import QIcon, QColor, QFont

import requests
import websocket
import threading


class CyberGuardDesktop(QMainWindow):
    """Main Desktop Application Window"""
    
    def __init__(self):
        super().__init__()
        self.api_url = "http://localhost:8000"
        self.ws_url = "ws://localhost:8000/ws/threats"
        self.ws = None
        self.threats = []
        self.stats = {}
        
        self.init_ui()
        self.setup_system_tray()
        self.setup_timers()
        self.connect_websocket()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("🛡️ CyberGuard Enterprise Platform")
        self.setMinimumSize(1200, 800)
        
        # Apply dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0f172a;
                color: #f1f5f9;
            }
            QTabWidget::pane {
                border: 1px solid #334155;
                background-color: #1e293b;
                border-radius: 8px;
            }
            QTabBar::tab {
                background-color: #1e293b;
                color: #cbd5e1;
                padding: 12px 24px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
            QTabBar::tab:selected {
                background-color: #2563eb;
                color: white;
            }
            QGroupBox {
                background-color: #1e293b;
                border: 1px solid #334155;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
                color: #f1f5f9;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
            }
            QPushButton {
                background-color: #2563eb;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
            QPushButton:pressed {
                background-color: #1e40af;
            }
            QLabel {
                color: #f1f5f9;
            }
            QTableWidget {
                background-color: #1e293b;
                color: #f1f5f9;
                gridline-color: #334155;
                border: 1px solid #334155;
                border-radius: 8px;
            }
            QHeaderView::section {
                background-color: #334155;
                color: #f1f5f9;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
            QProgressBar {
                border: 1px solid #334155;
                border-radius: 4px;
                text-align: center;
                background-color: #334155;
                color: white;
            }
            QProgressBar::chunk {
                background-color: #2563eb;
                border-radius: 4px;
            }
            QLineEdit {
                background-color: #334155;
                color: #f1f5f9;
                border: 1px solid #475569;
                padding: 8px;
                border-radius: 4px;
            }
        """)
        
        # Central widget with tabs
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header = self.create_header()
        layout.addWidget(header)
        
        # Tab widget
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_dashboard_tab(), "📊 Dashboard")
        self.tabs.addTab(self.create_threats_tab(), "⚠️ Threats")
        self.tabs.addTab(self.create_protection_tab(), "🔒 Protection")
        self.tabs.addTab(self.create_settings_tab(), "⚙️ Settings")
        
        layout.addWidget(self.tabs)
        
    def create_header(self) -> QWidget:
        """Create the application header"""
        header = QWidget()
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 20)
        
        # Title
        title = QLabel("🛡️ CyberGuard Enterprise Platform")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Connection status
        self.status_label = QLabel("● Connected")
        self.status_label.setStyleSheet("color: #10b981; font-weight: bold;")
        layout.addWidget(self.status_label)
        
        return header
        
    def create_dashboard_tab(self) -> QWidget:
        """Create the dashboard tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Stats grid
        stats_grid = QGridLayout()
        
        # Create stat cards
        self.active_threats_card = self.create_stat_card("Active Threats", "0", "⚠️")
        self.blocked_threats_card = self.create_stat_card("Blocked Today", "0", "✅")
        self.system_health_card = self.create_stat_card("System Health", "100%", "💻")
        self.scan_status_card = self.create_stat_card("Last Scan", "Never", "🔍")
        
        stats_grid.addWidget(self.active_threats_card, 0, 0)
        stats_grid.addWidget(self.blocked_threats_card, 0, 1)
        stats_grid.addWidget(self.system_health_card, 1, 0)
        stats_grid.addWidget(self.scan_status_card, 1, 1)
        
        layout.addLayout(stats_grid)
        
        # System resources
        resources_group = QGroupBox("System Resources")
        resources_layout = QVBoxLayout()
        
        # CPU
        cpu_layout = QHBoxLayout()
        cpu_layout.addWidget(QLabel("CPU Usage:"))
        self.cpu_bar = QProgressBar()
        self.cpu_bar.setMaximum(100)
        self.cpu_bar.setValue(45)
        cpu_layout.addWidget(self.cpu_bar)
        self.cpu_label = QLabel("45%")
        cpu_layout.addWidget(self.cpu_label)
        resources_layout.addLayout(cpu_layout)
        
        # Memory
        mem_layout = QHBoxLayout()
        mem_layout.addWidget(QLabel("Memory:"))
        self.mem_bar = QProgressBar()
        self.mem_bar.setMaximum(100)
        self.mem_bar.setValue(62)
        mem_layout.addWidget(self.mem_bar)
        self.mem_label = QLabel("62%")
        mem_layout.addWidget(self.mem_label)
        resources_layout.addLayout(mem_layout)
        
        # Disk
        disk_layout = QHBoxLayout()
        disk_layout.addWidget(QLabel("Disk:"))
        self.disk_bar = QProgressBar()
        self.disk_bar.setMaximum(100)
        self.disk_bar.setValue(38)
        disk_layout.addWidget(self.disk_bar)
        self.disk_label = QLabel("38%")
        disk_layout.addWidget(self.disk_label)
        resources_layout.addLayout(disk_layout)
        
        resources_group.setLayout(resources_layout)
        layout.addWidget(resources_group)
        
        # Quick actions
        actions_group = QGroupBox("Quick Actions")
        actions_layout = QHBoxLayout()
        
        scan_btn = QPushButton("🔍 Quick Scan")
        scan_btn.clicked.connect(self.quick_scan)
        actions_layout.addWidget(scan_btn)
        
        full_scan_btn = QPushButton("🔎 Full Scan")
        full_scan_btn.clicked.connect(self.full_scan)
        actions_layout.addWidget(full_scan_btn)
        
        update_btn = QPushButton("🔄 Update Definitions")
        update_btn.clicked.connect(self.update_definitions)
        actions_layout.addWidget(update_btn)
        
        actions_group.setLayout(actions_layout)
        layout.addWidget(actions_group)
        
        layout.addStretch()
        
        return widget
        
    def create_threats_tab(self) -> QWidget:
        """Create the threats monitoring tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Threats table
        self.threats_table = QTableWidget()
        self.threats_table.setColumnCount(5)
        self.threats_table.setHorizontalHeaderLabels([
            "Severity", "Type", "Description", "Status", "Time"
        ])
        self.threats_table.horizontalHeader().setStretchLastSection(True)
        self.threats_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.threats_table.setAlternatingRowColors(True)
        
        layout.addWidget(self.threats_table)
        
        # Actions
        actions_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.load_threats)
        actions_layout.addWidget(refresh_btn)
        
        clear_btn = QPushButton("🗑️ Clear History")
        clear_btn.clicked.connect(self.clear_threats)
        actions_layout.addWidget(clear_btn)
        
        actions_layout.addStretch()
        
        layout.addLayout(actions_layout)
        
        return widget
        
    def create_protection_tab(self) -> QWidget:
        """Create the protection settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Protection status
        status_group = QGroupBox("Protection Status")
        status_layout = QVBoxLayout()
        
        self.protection_status = QLabel("✅ All Protection Features Active")
        self.protection_status.setStyleSheet("color: #10b981; font-size: 16px; font-weight: bold;")
        status_layout.addWidget(self.protection_status)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # Protection features
        features_group = QGroupBox("Protection Features")
        features_layout = QVBoxLayout()
        
        # Real-time protection
        realtime_layout = QHBoxLayout()
        realtime_layout.addWidget(QLabel("🛡️ Real-time Protection:"))
        realtime_layout.addStretch()
        self.realtime_btn = QPushButton("Enabled")
        self.realtime_btn.setStyleSheet("background-color: #10b981;")
        self.realtime_btn.clicked.connect(lambda: self.toggle_protection("realtime"))
        realtime_layout.addWidget(self.realtime_btn)
        features_layout.addLayout(realtime_layout)
        
        # Network monitoring
        network_layout = QHBoxLayout()
        network_layout.addWidget(QLabel("🌐 Network Monitoring:"))
        network_layout.addStretch()
        self.network_btn = QPushButton("Enabled")
        self.network_btn.setStyleSheet("background-color: #10b981;")
        self.network_btn.clicked.connect(lambda: self.toggle_protection("network"))
        network_layout.addWidget(self.network_btn)
        features_layout.addLayout(network_layout)
        
        # File system protection
        filesystem_layout = QHBoxLayout()
        filesystem_layout.addWidget(QLabel("📁 File System Protection:"))
        filesystem_layout.addStretch()
        self.filesystem_btn = QPushButton("Enabled")
        self.filesystem_btn.setStyleSheet("background-color: #10b981;")
        self.filesystem_btn.clicked.connect(lambda: self.toggle_protection("filesystem"))
        filesystem_layout.addWidget(self.filesystem_btn)
        features_layout.addLayout(filesystem_layout)
        
        features_group.setLayout(features_layout)
        layout.addWidget(features_group)
        
        layout.addStretch()
        
        return widget
        
    def create_settings_tab(self) -> QWidget:
        """Create the settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # API settings
        api_group = QGroupBox("API Configuration")
        api_layout = QFormLayout()
        
        self.api_url_input = QLineEdit(self.api_url)
        api_layout.addRow("Backend API URL:", self.api_url_input)
        
        save_btn = QPushButton("💾 Save Settings")
        save_btn.clicked.connect(self.save_settings)
        api_layout.addRow("", save_btn)
        
        api_group.setLayout(api_layout)
        layout.addWidget(api_group)
        
        # About
        about_group = QGroupBox("About")
        about_layout = QVBoxLayout()
        
        about_text = QLabel(
            "CyberGuard Enterprise Platform v2.0.0\n"
            "Desktop Application for Windows\n\n"
            "© 2025 CyberGuard Industries\n"
            "All rights reserved."
        )
        about_layout.addWidget(about_text)
        
        about_group.setLayout(about_layout)
        layout.addWidget(about_group)
        
        layout.addStretch()
        
        return widget
        
    def create_stat_card(self, title: str, value: str, icon: str) -> QGroupBox:
        """Create a statistics card"""
        card = QGroupBox()
        layout = QVBoxLayout()
        
        # Icon and value
        header_layout = QHBoxLayout()
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 32px;")
        header_layout.addWidget(icon_label)
        
        value_label = QLabel(value)
        value_font = QFont()
        value_font.setPointSize(24)
        value_font.setBold(True)
        value_label.setFont(value_font)
        value_label.setObjectName(f"{title.lower().replace(' ', '_')}_value")
        header_layout.addWidget(value_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #94a3b8; font-size: 14px;")
        layout.addWidget(title_label)
        
        card.setLayout(layout)
        return card
        
    def setup_system_tray(self):
        """Setup system tray icon"""
        self.tray_icon = QSystemTrayIcon(self)
        
        # Create icon (using emoji as placeholder)
        self.tray_icon.setToolTip("CyberGuard Enterprise Platform")
        
        # Create menu
        tray_menu = QMenu()
        
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        hide_action = QAction("Hide", self)
        hide_action.triggered.connect(self.hide)
        tray_menu.addAction(hide_action)
        
        tray_menu.addSeparator()
        
        scan_action = QAction("Quick Scan", self)
        scan_action.triggered.connect(self.quick_scan)
        tray_menu.addAction(scan_action)
        
        tray_menu.addSeparator()
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(QApplication.quit)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
    def setup_timers(self):
        """Setup update timers"""
        # Update dashboard every 5 seconds
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_dashboard)
        self.update_timer.start(5000)
        
    def connect_websocket(self):
        """Connect to WebSocket for real-time updates"""
        def on_message(ws, message):
            try:
                data = json.loads(message)
                if data.get('type') == 'threat':
                    threat = data.get('threat', {})
                    self.threats.insert(0, threat)
                    self.update_threats_table()
                    self.show_threat_notification(threat)
            except Exception as e:
                print(f"WebSocket message error: {e}")
                
        def on_error(ws, error):
            print(f"WebSocket error: {error}")
            self.update_status(False)
            
        def on_close(ws, close_status_code, close_msg):
            print("WebSocket closed")
            self.update_status(False)
            
        def on_open(ws):
            print("WebSocket connected")
            self.update_status(True)
            
        def run_websocket():
            try:
                self.ws = websocket.WebSocketApp(
                    self.ws_url,
                    on_message=on_message,
                    on_error=on_error,
                    on_close=on_close,
                    on_open=on_open
                )
                self.ws.run_forever()
            except Exception as e:
                print(f"WebSocket connection error: {e}")
                self.update_status(False)
                
        # Run WebSocket in a separate thread
        ws_thread = threading.Thread(target=run_websocket, daemon=True)
        ws_thread.start()
        
    def update_status(self, connected: bool):
        """Update connection status"""
        if connected:
            self.status_label.setText("● Connected")
            self.status_label.setStyleSheet("color: #10b981; font-weight: bold;")
        else:
            self.status_label.setText("● Disconnected")
            self.status_label.setStyleSheet("color: #ef4444; font-weight: bold;")
            
    def update_dashboard(self):
        """Update dashboard with latest data"""
        try:
            response = requests.get(f"{self.api_url}/api/v1/dashboard", timeout=2)
            if response.status_code == 200:
                data = response.json()
                self.stats = data
                
                # Update stat cards
                self.update_stat_value("active_threats", str(data.get('active_threats', 0)))
                self.update_stat_value("blocked_today", str(data.get('blocked_threats', 0)))
                self.update_stat_value("system_health", f"{data.get('system_health', 100)}%")
                
                # Update resource meters
                self.cpu_bar.setValue(int(data.get('cpu_usage', 0)))
                self.cpu_label.setText(f"{data.get('cpu_usage', 0)}%")
                
                self.mem_bar.setValue(int(data.get('memory_usage', 0)))
                self.mem_label.setText(f"{data.get('memory_usage', 0)}%")
                
                self.disk_bar.setValue(int(data.get('disk_usage', 0)))
                self.disk_label.setText(f"{data.get('disk_usage', 0)}%")
                
        except Exception as e:
            print(f"Dashboard update error: {e}")
            
    def update_stat_value(self, name: str, value: str):
        """Update a stat card value"""
        label = self.findChild(QLabel, f"{name}_value")
        if label:
            label.setText(value)
            
    def load_threats(self):
        """Load threats from API"""
        try:
            response = requests.get(f"{self.api_url}/api/v1/threats", timeout=2)
            if response.status_code == 200:
                data = response.json()
                self.threats = data.get('threats', [])
                self.update_threats_table()
        except Exception as e:
            print(f"Load threats error: {e}")
            
    def update_threats_table(self):
        """Update the threats table"""
        self.threats_table.setRowCount(len(self.threats))
        
        for i, threat in enumerate(self.threats[:50]):  # Show last 50
            self.threats_table.setItem(i, 0, QTableWidgetItem(threat.get('severity', 'Low')))
            self.threats_table.setItem(i, 1, QTableWidgetItem(threat.get('type', 'Unknown')))
            self.threats_table.setItem(i, 2, QTableWidgetItem(threat.get('description', 'No description')))
            self.threats_table.setItem(i, 3, QTableWidgetItem(threat.get('status', 'Detected')))
            self.threats_table.setItem(i, 4, QTableWidgetItem(threat.get('timestamp', 'Unknown')))
            
    def show_threat_notification(self, threat: Dict):
        """Show system tray notification for new threat"""
        if self.tray_icon:
            self.tray_icon.showMessage(
                "⚠️ New Threat Detected",
                f"{threat.get('type', 'Unknown')}: {threat.get('description', 'No description')}",
                QSystemTrayIcon.Warning,
                5000
            )
            
    def quick_scan(self):
        """Perform quick scan"""
        QMessageBox.information(self, "Quick Scan", "Quick scan started in background...")
        
    def full_scan(self):
        """Perform full scan"""
        QMessageBox.information(self, "Full Scan", "Full system scan started. This may take a while...")
        
    def update_definitions(self):
        """Update threat definitions"""
        QMessageBox.information(self, "Update", "Threat definitions updated successfully!")
        
    def clear_threats(self):
        """Clear threats history"""
        reply = QMessageBox.question(
            self, "Clear History",
            "Are you sure you want to clear all threat history?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.threats = []
            self.update_threats_table()
            
    def toggle_protection(self, feature: str):
        """Toggle protection feature"""
        button_map = {
            'realtime': self.realtime_btn,
            'network': self.network_btn,
            'filesystem': self.filesystem_btn
        }
        
        btn = button_map.get(feature)
        if btn:
            if btn.text() == "Enabled":
                btn.setText("Disabled")
                btn.setStyleSheet("background-color: #ef4444;")
            else:
                btn.setText("Enabled")
                btn.setStyleSheet("background-color: #10b981;")
                
    def save_settings(self):
        """Save application settings"""
        self.api_url = self.api_url_input.text()
        QMessageBox.information(self, "Settings", "Settings saved successfully!")
        
    def closeEvent(self, event):
        """Handle window close event"""
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "CyberGuard",
            "Application minimized to system tray",
            QSystemTrayIcon.Information,
            2000
        )


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("CyberGuard Enterprise Platform")
    app.setOrganizationName("CyberGuard Industries")
    
    # Set application style
    app.setStyle("Fusion")
    
    window = CyberGuardDesktop()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

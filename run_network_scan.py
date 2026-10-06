#!/usr/bin/env python
"""
Script to manually trigger a network scan.
Run with: python run_network_scan.py
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asset_tracker.settings')
django.setup()

from power_monitoring.models import ScanJob
from power_monitoring.services.network_scanner_service import NetworkScannerService

print("Creating scan job...")
scan_job = ScanJob.objects.create(status='pending')

print(f"Starting scan (Job ID: {scan_job.id})...")
try:
    result = NetworkScannerService.execute_scan(scan_job)
    print(f"\nScan completed successfully!")
    print(f"Total IPs scanned: {result['total_ips']}")
    print(f"Online: {result['online']}")
    print(f"Offline: {result['offline']}")
    print(f"Tracked assets: {result['tracked']}")
    print(f"Discovered IPs: {result['discovered']}")
except Exception as e:
    print(f"\nScan failed: {e}")

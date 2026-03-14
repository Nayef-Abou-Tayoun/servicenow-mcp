"""
Demo script showing how to create incidents with custom fields.

This example demonstrates using the extended incident tools that support
custom fields defined in config/incident_custom_fields.yaml.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from servicenow_mcp.auth.auth_manager import AuthManager
from servicenow_mcp.utils.config import ServerConfig
from servicenow_mcp.tools.incident_tools_extended import (
    create_incident_extended,
    ExtendedCreateIncidentParams,
)


def main():
    """Main demo function."""
    
    # Initialize configuration
    config = ServerConfig(
        instance_url=os.getenv("SERVICENOW_INSTANCE_URL", "https://your-instance.service-now.com"),
        timeout=30,
    )
    
    # Initialize auth manager
    auth_manager = AuthManager(config)
    
    print("=" * 60)
    print("ServiceNow Incident Creation with Custom Fields Demo")
    print("=" * 60)
    
    # Example 1: Create incident with standard fields only
    print("\n1. Creating incident with standard fields...")
    params1 = ExtendedCreateIncidentParams(
        short_description="Test incident - standard fields only",
        description="This is a test incident using only standard ServiceNow fields",
        priority="3",
        impact="2",
        urgency="2",
    )
    
    result1 = create_incident_extended(config, auth_manager, params1)
    print(f"   Result: {result1.message}")
    if result1.success:
        print(f"   Incident Number: {result1.incident_number}")
        print(f"   Incident ID: {result1.incident_id}")
    
    # Example 2: Create incident with custom fields
    print("\n2. Creating incident with custom fields...")
    params2 = ExtendedCreateIncidentParams(
        short_description="Test incident - with custom fields",
        description="This incident includes custom fields from the YAML config",
        priority="2",
        impact="2",
        urgency="2",
        # Custom fields (defined in config/incident_custom_fields.yaml)
        location="Building A, Floor 3",
        business_service="Email Service",
        cmdb_ci="MAIL-SERVER-01",
    )
    
    result2 = create_incident_extended(config, auth_manager, params2)
    print(f"   Result: {result2.message}")
    if result2.success:
        print(f"   Incident Number: {result2.incident_number}")
        print(f"   Incident ID: {result2.incident_id}")
    
    # Example 3: Create incident with network/telecom fields (like your payload)
    print("\n3. Creating network quality degradation incident...")
    params3 = ExtendedCreateIncidentParams(
        short_description="Network quality degradation - Area 403 (eNB 403-17, Sector B)",
        description="Customer CUST-883420 reports intermittent service issues near 43.6486,-79.3853. "
                   "KPIs: RSRP -118 dBm, SINR 3 dB, RSRQ -17 dB, Packet Loss 6.1%, Drop Rate 7.4%, "
                   "Throughput 3.8/0.6 Mbps. Time window: 2026-03-11 18:30–22:45. "
                   "Nearest cell: eNB 403-17, Sector B (PCI 287).",
        category="network",
        subcategory="radio_access",
        impact="2",
        urgency="2",
        caller_id="CUST-883420",
        assignment_group="RAN Operations - Area 403",
        # Custom fields
        cmdb_ci="CELL-ENB-403-17-B",
        work_notes="Created by watsonx Orchestrate via MCP. Next: Severity analysis via ODM.",
        # Network-specific custom fields
        u_area="403",
        u_kpi_rsrp=-118.0,
        u_kpi_sinr=3.0,
        u_kpi_rsrq=-17.0,
        u_packet_loss=6.1,
        u_drop_rate=7.4,
        u_throughput_dl_mbps=3.8,
        u_throughput_ul_mbps=0.6,
        u_case_type="Network Quality Degradation",
    )
    
    result3 = create_incident_extended(config, auth_manager, params3)
    print(f"   Result: {result3.message}")
    if result3.success:
        print(f"   Incident Number: {result3.incident_number}")
        print(f"   Incident ID: {result3.incident_id}")
    
    print("\n" + "=" * 60)
    print("Demo completed!")
    print("=" * 60)
    print("\nNote: Custom fields are automatically loaded from:")
    print("      config/incident_custom_fields.yaml")
    print("\nTo add more custom fields:")
    print("  1. Add field definition to config/incident_custom_fields.yaml")
    print("  2. Add field to ExtendedCreateIncidentParams in incident_tools_extended.py")
    print("  3. Use the field when creating incidents")


if __name__ == "__main__":
    main()

# Made with Bob

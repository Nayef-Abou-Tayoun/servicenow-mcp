# Custom Incident Fields - Quick Start Guide

This ServiceNow MCP server now supports custom incident fields that can be enabled via environment variable.

## Quick Setup

### 1. Enable Custom Fields

Add this to your `.env` file or Docker environment:

```bash
USE_EXTENDED_INCIDENT_FIELDS=true
```

### 2. Deploy/Restart Container

```bash
# If using Docker
docker-compose down
docker-compose up -d

# Or rebuild
docker build -t servicenow-mcp .
docker run -e USE_EXTENDED_INCIDENT_FIELDS=true \
           -e SERVICENOW_INSTANCE_URL="https://your-instance.service-now.com" \
           -e SERVICENOW_USERNAME="your-username" \
           -e SERVICENOW_PASSWORD="your-password" \
           -p 8080:8080 \
           servicenow-mcp
```

### 3. Use Custom Fields

Once enabled, the `create_incident` tool accepts these additional fields:

#### Standard Custom Fields:
- `location` - Location of the incident
- `business_service` - Business service affected
- `cmdb_ci` - Configuration item
- `work_notes` - Work notes to add

#### Network/Telecom Fields:
- `u_area` - Network area identifier (e.g., "403")
- `u_kpi_rsrp` - Reference Signal Received Power in dBm (e.g., -118)
- `u_kpi_sinr` - Signal to Interference plus Noise Ratio in dB (e.g., 3)
- `u_kpi_rsrq` - Reference Signal Received Quality in dB (e.g., -17)
- `u_packet_loss` - Packet loss percentage (e.g., 6.1)
- `u_drop_rate` - Call drop rate percentage (e.g., 7.4)
- `u_throughput_dl_mbps` - Downlink throughput in Mbps (e.g., 3.8)
- `u_throughput_ul_mbps` - Uplink throughput in Mbps (e.g., 0.6)
- `u_case_type` - Case type classification (e.g., "Network Quality Degradation")

## Example Usage

### With watsonx Orchestrate:

```json
{
  "target": "servicenow.incident.create",
  "payload": {
    "short_description": "Network quality degradation - Area 403",
    "description": "Customer reports intermittent service issues",
    "category": "network",
    "subcategory": "radio_access",
    "impact": "2",
    "urgency": "2",
    "cmdb_ci": "CELL-ENB-403-17-B",
    "u_area": "403",
    "u_kpi_rsrp": -118,
    "u_kpi_sinr": 3,
    "u_kpi_rsrq": -17,
    "u_packet_loss": 6.1,
    "u_drop_rate": 7.4,
    "u_throughput_dl_mbps": 3.8,
    "u_throughput_ul_mbps": 0.6,
    "u_case_type": "Network Quality Degradation"
  }
}
```

## Disabling Custom Fields

To disable custom fields and use only standard ServiceNow fields:

```bash
USE_EXTENDED_INCIDENT_FIELDS=false
```

Or simply remove the environment variable (defaults to `false`).

## Important Notes

- ✅ **Backward Compatible**: When disabled, the tool works exactly as before
- ✅ **Optional Fields**: All custom fields are optional
- ✅ **No Code Changes**: Toggle via environment variable only
- ⚠️ **ServiceNow Schema**: Ensure your ServiceNow instance has these custom fields defined

## Troubleshooting

### Custom fields not appearing in tool schema?

1. Check environment variable is set: `USE_EXTENDED_INCIDENT_FIELDS=true`
2. Restart the container/service
3. Verify in logs that extended mode is enabled

### Fields not saving to ServiceNow?

1. Verify the custom fields exist in your ServiceNow instance
2. Check field names match exactly (case-sensitive)
3. Ensure user has permissions to write to these fields

## More Information

- Full documentation: [`docs/custom_incident_fields.md`](docs/custom_incident_fields.md)
- Configuration file: [`config/incident_custom_fields.yaml`](config/incident_custom_fields.yaml)
- Example script: [`examples/incident_with_custom_fields_demo.py`](examples/incident_with_custom_fields_demo.py)
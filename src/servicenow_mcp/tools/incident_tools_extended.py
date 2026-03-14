"""
Extended incident tools with custom fields support.

This module provides wrapper functions that extend the base incident tools
with custom field support from configuration files.
"""

import logging
from typing import Optional

import requests
from pydantic import BaseModel, Field

from servicenow_mcp.auth.auth_manager import AuthManager
from servicenow_mcp.utils.config import ServerConfig
from servicenow_mcp.utils.custom_fields import apply_custom_fields

logger = logging.getLogger(__name__)


class ExtendedCreateIncidentParams(BaseModel):
    """Extended parameters for creating an incident with custom fields."""

    # Standard ServiceNow fields
    short_description: str = Field(..., description="Short description of the incident")
    description: Optional[str] = Field(None, description="Detailed description of the incident")
    caller_id: Optional[str] = Field(None, description="User who reported the incident")
    category: Optional[str] = Field(None, description="Category of the incident")
    subcategory: Optional[str] = Field(None, description="Subcategory of the incident")
    priority: Optional[str] = Field(None, description="Priority of the incident")
    impact: Optional[str] = Field(None, description="Impact of the incident")
    urgency: Optional[str] = Field(None, description="Urgency of the incident")
    assigned_to: Optional[str] = Field(None, description="User assigned to the incident")
    assignment_group: Optional[str] = Field(None, description="Group assigned to the incident")
    
    # Standard custom fields
    location: Optional[str] = Field(None, description="Location of the incident")
    business_service: Optional[str] = Field(None, description="Business service affected")
    cmdb_ci: Optional[str] = Field(None, description="Configuration item")
    work_notes: Optional[str] = Field(None, description="Work notes to add to the incident")
    
    # Network/Telecom specific custom fields
    u_area: Optional[str] = Field(None, description="Network area identifier")
    u_kpi_rsrp: Optional[float] = Field(None, description="KPI - Reference Signal Received Power (dBm)")
    u_kpi_sinr: Optional[float] = Field(None, description="KPI - Signal to Interference plus Noise Ratio (dB)")
    u_kpi_rsrq: Optional[float] = Field(None, description="KPI - Reference Signal Received Quality (dB)")
    u_packet_loss: Optional[float] = Field(None, description="Packet loss percentage")
    u_drop_rate: Optional[float] = Field(None, description="Call drop rate percentage")
    u_throughput_dl_mbps: Optional[float] = Field(None, description="Downlink throughput in Mbps")
    u_throughput_ul_mbps: Optional[float] = Field(None, description="Uplink throughput in Mbps")
    u_case_type: Optional[str] = Field(None, description="Case type classification")
    
    class Config:
        extra = "allow"  # Allow additional fields not explicitly defined


class IncidentResponse(BaseModel):
    """Response from incident operations."""

    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Message describing the result")
    incident_id: Optional[str] = Field(None, description="ID of the affected incident")
    incident_number: Optional[str] = Field(None, description="Number of the affected incident")


def create_incident_extended(
    config: ServerConfig,
    auth_manager: AuthManager,
    params: ExtendedCreateIncidentParams,
) -> IncidentResponse:
    """
    Create a new incident in ServiceNow with custom fields support.
    
    This function extends the base create_incident functionality by automatically
    applying custom fields defined in config/incident_custom_fields.yaml.

    Args:
        config: Server configuration.
        auth_manager: Authentication manager.
        params: Extended parameters including custom fields.

    Returns:
        Response with the created incident details.
    """
    api_url = f"{config.api_url}/table/incident"

    # Build request data with standard fields
    data = {
        "short_description": params.short_description,
    }

    # Add standard optional fields
    if params.description:
        data["description"] = params.description
    if params.caller_id:
        data["caller_id"] = params.caller_id
    if params.category:
        data["category"] = params.category
    if params.subcategory:
        data["subcategory"] = params.subcategory
    if params.priority:
        data["priority"] = params.priority
    if params.impact:
        data["impact"] = params.impact
    if params.urgency:
        data["urgency"] = params.urgency
    if params.assigned_to:
        data["assigned_to"] = params.assigned_to
    if params.assignment_group:
        data["assignment_group"] = params.assignment_group

    # Apply custom fields from configuration
    data = apply_custom_fields(data, params)

    # Make request
    try:
        response = requests.post(
            api_url,
            json=data,
            headers=auth_manager.get_headers(),
            timeout=config.timeout,
        )
        response.raise_for_status()

        result = response.json().get("result", {})

        return IncidentResponse(
            success=True,
            message="Incident created successfully",
            incident_id=result.get("sys_id"),
            incident_number=result.get("number"),
        )

    except requests.RequestException as e:
        logger.error(f"Failed to create incident: {e}")
        return IncidentResponse(
            success=False,
            message=f"Failed to create incident: {str(e)}",
        )

# Made with Bob

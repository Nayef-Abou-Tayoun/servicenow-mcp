"""
Incident tools for the ServiceNow MCP server.

This module provides tools for managing incidents in ServiceNow.
"""

import json
import logging
import os
from typing import Optional, List

import requests
from pydantic import BaseModel, Field

from servicenow_mcp.auth.auth_manager import AuthManager
from servicenow_mcp.utils.config import ServerConfig

logger = logging.getLogger(__name__)


def _use_extended_fields() -> bool:
    """Check if extended incident fields are enabled via environment variable."""
    return os.getenv("USE_EXTENDED_INCIDENT_FIELDS", "false").lower() == "true"


class CreateIncidentParams(BaseModel):
    """Parameters for creating an incident."""

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
    
    # Extended fields (enabled via USE_EXTENDED_INCIDENT_FIELDS=true)
    location: Optional[str] = Field(None, description="Location of the incident")
    business_service: Optional[str] = Field(None, description="Business service affected")
    cmdb_ci: Optional[str] = Field(None, description="Configuration item")
    work_notes: Optional[str] = Field(None, description="Work notes to add to the incident")
    u_area: Optional[str] = Field(None, description="Network area identifier (string)", json_schema_extra={"type": "string"})
    u_kpi_rsrp: Optional[str] = Field(None, description="KPI - Reference Signal Received Power in dBm (string, e.g. '-85.0')", json_schema_extra={"type": "string"})
    u_kpi_sinr: Optional[str] = Field(None, description="KPI - Signal to Interference plus Noise Ratio in dB (string, e.g. '5.0')", json_schema_extra={"type": "string"})
    u_kpi_rsrq: Optional[str] = Field(None, description="KPI - Reference Signal Received Quality in dB (string, e.g. '-10.0')", json_schema_extra={"type": "string"})
    u_packet_loss: Optional[str] = Field(None, description="Packet loss percentage (string, e.g. '2.5')", json_schema_extra={"type": "string"})
    u_drop_rate: Optional[str] = Field(None, description="Call drop rate percentage (string, e.g. '1.2')", json_schema_extra={"type": "string"})
    u_throughput_dl_mbps: Optional[str] = Field(None, description="Downlink throughput in Mbps (string, e.g. '100.5')", json_schema_extra={"type": "string"})
    u_throughput_ul_mbps: Optional[str] = Field(None, description="Uplink throughput in Mbps (string, e.g. '50.3')", json_schema_extra={"type": "string"})
    u_case_type: Optional[str] = Field(None, description="Case type classification (string)", json_schema_extra={"type": "string"})
    u_customer_impact_note0: Optional[str] = Field(None, description="Customer impact notes (string)", json_schema_extra={"type": "string"})
    u_network_quality_score: Optional[str] = Field(None, description="Network quality score as float (string, e.g. '85.5')", json_schema_extra={"type": "string"})
    u_network_quality_interpretation: Optional[str] = Field(None, description="Network quality interpretation (string)", json_schema_extra={"type": "string"})
    u_context_environment_impact_score: Optional[str] = Field(None, description="Context environment impact score as float (string, e.g. '75.0')", json_schema_extra={"type": "string"})
    u_context_notes: Optional[str] = Field(None, description="Context notes (string)", json_schema_extra={"type": "string"})
    u_context_score: Optional[str] = Field(None, description="Context score as float (string, e.g. '80.0')", json_schema_extra={"type": "string"})
    u_incident_priority: Optional[str] = Field(None, description="Incident priority (string)", json_schema_extra={"type": "string"})
    u_final_severity_score: Optional[str] = Field(None, description="Final severity score as float (string, e.g. '90.5')", json_schema_extra={"type": "string"})
    
    class Config:
        extra = "allow"  # Allow additional fields not explicitly defined


class UpdateIncidentParams(BaseModel):
    """Parameters for updating an incident."""

    incident_id: str = Field(..., description="Incident ID or sys_id")
    short_description: Optional[str] = Field(None, description="Short description of the incident")
    description: Optional[str] = Field(None, description="Detailed description of the incident")
    state: Optional[str] = Field(None, description="State of the incident")
    category: Optional[str] = Field(None, description="Category of the incident")
    subcategory: Optional[str] = Field(None, description="Subcategory of the incident")
    priority: Optional[str] = Field(None, description="Priority of the incident")
    impact: Optional[str] = Field(None, description="Impact of the incident")
    urgency: Optional[str] = Field(None, description="Urgency of the incident")
    assigned_to: Optional[str] = Field(None, description="User assigned to the incident")
    assignment_group: Optional[str] = Field(None, description="Group assigned to the incident")
    work_notes: Optional[str] = Field(None, description="Work notes to add to the incident")
    close_notes: Optional[str] = Field(None, description="Close notes to add to the incident")
    close_code: Optional[str] = Field(None, description="Close code for the incident")
    
    # Extended fields (enabled via USE_EXTENDED_INCIDENT_FIELDS=true)
    location: Optional[str] = Field(None, description="Location of the incident")
    business_service: Optional[str] = Field(None, description="Business service affected")
    cmdb_ci: Optional[str] = Field(None, description="Configuration item")
    u_area: Optional[str] = Field(None, description="Network area identifier (string)", json_schema_extra={"type": "string"})
    u_kpi_rsrp: Optional[str] = Field(None, description="KPI - Reference Signal Received Power in dBm (string, e.g. '-85.0')", json_schema_extra={"type": "string"})
    u_kpi_sinr: Optional[str] = Field(None, description="KPI - Signal to Interference plus Noise Ratio in dB (string, e.g. '5.0')", json_schema_extra={"type": "string"})
    u_kpi_rsrq: Optional[str] = Field(None, description="KPI - Reference Signal Received Quality in dB (string, e.g. '-10.0')", json_schema_extra={"type": "string"})
    u_packet_loss: Optional[str] = Field(None, description="Packet loss percentage (string, e.g. '2.5')", json_schema_extra={"type": "string"})
    u_drop_rate: Optional[str] = Field(None, description="Call drop rate percentage (string, e.g. '1.2')", json_schema_extra={"type": "string"})
    u_throughput_dl_mbps: Optional[str] = Field(None, description="Downlink throughput in Mbps (string, e.g. '100.5')", json_schema_extra={"type": "string"})
    u_throughput_ul_mbps: Optional[str] = Field(None, description="Uplink throughput in Mbps (string, e.g. '50.3')", json_schema_extra={"type": "string"})
    u_case_type: Optional[str] = Field(None, description="Case type classification (string)", json_schema_extra={"type": "string"})
    u_customer_impact_note0: Optional[str] = Field(None, description="Customer impact notes (string)", json_schema_extra={"type": "string"})
    u_network_quality_score: Optional[str] = Field(None, description="Network quality score as float (string, e.g. '85.5')", json_schema_extra={"type": "string"})
    u_network_quality_interpretation: Optional[str] = Field(None, description="Network quality interpretation (string)", json_schema_extra={"type": "string"})
    u_context_environment_impact_score: Optional[str] = Field(None, description="Context environment impact score as float (string, e.g. '75.0')", json_schema_extra={"type": "string"})
    u_context_notes: Optional[str] = Field(None, description="Context notes (string)", json_schema_extra={"type": "string"})
    u_context_score: Optional[str] = Field(None, description="Context score as float (string, e.g. '80.0')", json_schema_extra={"type": "string"})
    u_incident_priority: Optional[str] = Field(None, description="Incident priority (string)", json_schema_extra={"type": "string"})
    u_final_severity_score: Optional[str] = Field(None, description="Final severity score as float (string, e.g. '90.5')", json_schema_extra={"type": "string"})
    
    class Config:
        extra = "allow"  # Allow additional fields not explicitly defined


class AddCommentParams(BaseModel):
    """Parameters for adding a comment to an incident."""

    incident_id: str = Field(..., description="Incident ID or sys_id")
    comment: str = Field(..., description="Comment to add to the incident")
    is_work_note: bool = Field(False, description="Whether the comment is a work note")


class ResolveIncidentParams(BaseModel):
    """Parameters for resolving an incident."""

    incident_id: str = Field(..., description="Incident ID or sys_id")
    resolution_code: str = Field(..., description="Resolution code for the incident")
    resolution_notes: str = Field(..., description="Resolution notes for the incident")


class ListIncidentsParams(BaseModel):
    """Parameters for listing incidents."""
    
    limit: int = Field(10, description="Maximum number of incidents to return")
    offset: int = Field(0, description="Offset for pagination")
    state: Optional[str] = Field(None, description="Filter by incident state")
    assigned_to: Optional[str] = Field(None, description="Filter by assigned user")
    category: Optional[str] = Field(None, description="Filter by category")
    query: Optional[str] = Field(None, description="Search query for incidents")


class GetIncidentByNumberParams(BaseModel):
    """Parameters for fetching an incident by its number."""

    incident_number: str = Field(..., description="The number of the incident to fetch")


class IncidentResponse(BaseModel):
    """Response from incident operations."""

    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Message describing the result")
    incident_id: Optional[str] = Field(None, description="ID of the affected incident")
    incident_number: Optional[str] = Field(None, description="Number of the affected incident")


def create_incident(
    config: ServerConfig,
    auth_manager: AuthManager,
    params: CreateIncidentParams,
) -> IncidentResponse:
    """
    Create a new incident in ServiceNow.

    Args:
        config: Server configuration.
        auth_manager: Authentication manager.
        params: Parameters for creating the incident.

    Returns:
        Response with the created incident details.
    """
    api_url = f"{config.api_url}/table/incident"

    # Build request data
    data = {
        "short_description": params.short_description,
    }

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
    
    # Add extended fields if enabled
    if _use_extended_fields():
        logger.info("Extended incident fields enabled - adding custom fields to request")
        
        # Log all received parameters for debugging
        logger.info(f"Received params: location={params.location}, business_service={params.business_service}, "
                   f"cmdb_ci={params.cmdb_ci}, work_notes={params.work_notes}, u_area={params.u_area}, "
                   f"u_kpi_rsrp={params.u_kpi_rsrp}, u_kpi_sinr={params.u_kpi_sinr}, u_kpi_rsrq={params.u_kpi_rsrq}, "
                   f"u_packet_loss={params.u_packet_loss}, u_drop_rate={params.u_drop_rate}, "
                   f"u_throughput_dl_mbps={params.u_throughput_dl_mbps}, u_throughput_ul_mbps={params.u_throughput_ul_mbps}, "
                   f"u_case_type={params.u_case_type}, u_customer_impact_note0={params.u_customer_impact_note0}, "
                   f"u_network_quality_score={params.u_network_quality_score}, u_network_quality_interpretation={params.u_network_quality_interpretation}, "
                   f"u_context_environment_impact_score={params.u_context_environment_impact_score}, u_context_notes={params.u_context_notes}, "
                   f"u_context_score={params.u_context_score}, u_incident_priority={params.u_incident_priority}, "
                   f"u_final_severity_score={params.u_final_severity_score}")
        
        if params.location:
            data["location"] = params.location
            logger.info(f"Added location: {params.location}")
        if params.business_service:
            data["business_service"] = params.business_service
            logger.info(f"Added business_service: {params.business_service}")
        if params.cmdb_ci:
            data["cmdb_ci"] = params.cmdb_ci
            logger.info(f"Added cmdb_ci: {params.cmdb_ci}")
        if params.work_notes:
            data["work_notes"] = params.work_notes
            logger.info(f"Added work_notes: {params.work_notes}")
        if params.u_area:
            data["u_area"] = params.u_area
            logger.info(f"Added u_area: {params.u_area}")
        if params.u_kpi_rsrp:
            data["u_kpi_rsrp"] = params.u_kpi_rsrp
            logger.info(f"Added u_kpi_rsrp: {params.u_kpi_rsrp}")
        if params.u_kpi_sinr:
            data["u_kpi_sinr"] = params.u_kpi_sinr
            logger.info(f"Added u_kpi_sinr: {params.u_kpi_sinr}")
        if params.u_kpi_rsrq:
            data["u_kpi_rsrq"] = params.u_kpi_rsrq
            logger.info(f"Added u_kpi_rsrq: {params.u_kpi_rsrq}")
        if params.u_packet_loss:
            data["u_packet_loss"] = params.u_packet_loss
            logger.info(f"Added u_packet_loss: {params.u_packet_loss}")
        if params.u_drop_rate:
            data["u_drop_rate"] = params.u_drop_rate
            logger.info(f"Added u_drop_rate: {params.u_drop_rate}")
        if params.u_throughput_dl_mbps:
            data["u_throughput_dl_mbps"] = params.u_throughput_dl_mbps
            logger.info(f"Added u_throughput_dl_mbps: {params.u_throughput_dl_mbps}")
        if params.u_throughput_ul_mbps:
            data["u_throughput_ul_mbps"] = params.u_throughput_ul_mbps
            logger.info(f"Added u_throughput_ul_mbps: {params.u_throughput_ul_mbps}")
        if params.u_case_type:
            data["u_case_type"] = params.u_case_type
            logger.info(f"Added u_case_type: {params.u_case_type}")
        if params.u_customer_impact_note0:
            data["u_customer_impact_note0"] = params.u_customer_impact_note0
            logger.info(f"Added u_customer_impact_note0: {params.u_customer_impact_note0}")
        if params.u_network_quality_score:
            data["u_network_quality_score"] = params.u_network_quality_score
            logger.info(f"Added u_network_quality_score: {params.u_network_quality_score}")
        if params.u_network_quality_interpretation:
            data["u_network_quality_interpretation"] = params.u_network_quality_interpretation
            logger.info(f"Added u_network_quality_interpretation: {params.u_network_quality_interpretation}")
        if params.u_context_environment_impact_score:
            data["u_context_environment_impact_score"] = params.u_context_environment_impact_score
            logger.info(f"Added u_context_environment_impact_score: {params.u_context_environment_impact_score}")
        if params.u_context_notes:
            data["u_context_notes"] = params.u_context_notes
            logger.info(f"Added u_context_notes: {params.u_context_notes}")
        if params.u_context_score:
            data["u_context_score"] = params.u_context_score
            logger.info(f"Added u_context_score: {params.u_context_score}")
        if params.u_incident_priority:
            data["u_incident_priority"] = params.u_incident_priority
            logger.info(f"Added u_incident_priority: {params.u_incident_priority}")
        if params.u_final_severity_score:
            data["u_final_severity_score"] = params.u_final_severity_score
            logger.info(f"Added u_final_severity_score: {params.u_final_severity_score}")
        
        logger.info(f"Final data being sent to ServiceNow: {json.dumps(data, indent=2)}")

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


def update_incident(
    config: ServerConfig,
    auth_manager: AuthManager,
    params: UpdateIncidentParams,
) -> IncidentResponse:
    """
    Update an existing incident in ServiceNow.

    Args:
        config: Server configuration.
        auth_manager: Authentication manager.
        params: Parameters for updating the incident.

    Returns:
        Response with the updated incident details.
    """
    # Determine if incident_id is a number or sys_id
    incident_id = params.incident_id
    if len(incident_id) == 32 and all(c in "0123456789abcdef" for c in incident_id):
        # This is likely a sys_id
        api_url = f"{config.api_url}/table/incident/{incident_id}"
    else:
        # This is likely an incident number
        # First, we need to get the sys_id
        try:
            query_url = f"{config.api_url}/table/incident"
            query_params = {
                "sysparm_query": f"number={incident_id}",
                "sysparm_limit": 1,
            }

            response = requests.get(
                query_url,
                params=query_params,
                headers=auth_manager.get_headers(),
                timeout=config.timeout,
            )
            response.raise_for_status()

            result = response.json().get("result", [])
            if not result:
                return IncidentResponse(
                    success=False,
                    message=f"Incident not found: {incident_id}",
                )

            incident_id = result[0].get("sys_id")
            api_url = f"{config.api_url}/table/incident/{incident_id}"

        except requests.RequestException as e:
            logger.error(f"Failed to find incident: {e}")
            return IncidentResponse(
                success=False,
                message=f"Failed to find incident: {str(e)}",
            )

    # Build request data
    data = {}

    if params.short_description:
        data["short_description"] = params.short_description
    if params.description:
        data["description"] = params.description
    if params.state:
        data["state"] = params.state
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
    if params.work_notes:
        data["work_notes"] = params.work_notes
    if params.close_notes:
        data["close_notes"] = params.close_notes
    if params.close_code:
        data["close_code"] = params.close_code
    
    # Add extended fields if enabled
    if _use_extended_fields():
        logger.info("Extended incident fields enabled - adding custom fields to update request")
        if params.location:
            data["location"] = params.location
        if params.business_service:
            data["business_service"] = params.business_service
        if params.cmdb_ci:
            data["cmdb_ci"] = params.cmdb_ci
        if params.u_area:
            data["u_area"] = params.u_area
        if params.u_kpi_rsrp:
            data["u_kpi_rsrp"] = params.u_kpi_rsrp
        if params.u_kpi_sinr:
            data["u_kpi_sinr"] = params.u_kpi_sinr
        if params.u_kpi_rsrq:
            data["u_kpi_rsrq"] = params.u_kpi_rsrq
        if params.u_packet_loss:
            data["u_packet_loss"] = params.u_packet_loss
        if params.u_drop_rate:
            data["u_drop_rate"] = params.u_drop_rate
        if params.u_throughput_dl_mbps:
            data["u_throughput_dl_mbps"] = params.u_throughput_dl_mbps
        if params.u_throughput_ul_mbps:
            data["u_throughput_ul_mbps"] = params.u_throughput_ul_mbps
        if params.u_case_type:
            data["u_case_type"] = params.u_case_type
        if params.u_customer_impact_note0:
            data["u_customer_impact_note0"] = params.u_customer_impact_note0
        if params.u_network_quality_score:
            data["u_network_quality_score"] = params.u_network_quality_score
        if params.u_network_quality_interpretation:
            data["u_network_quality_interpretation"] = params.u_network_quality_interpretation
        if params.u_context_environment_impact_score:
            data["u_context_environment_impact_score"] = params.u_context_environment_impact_score
        if params.u_context_notes:
            data["u_context_notes"] = params.u_context_notes
        if params.u_context_score:
            data["u_context_score"] = params.u_context_score
        if params.u_incident_priority:
            data["u_incident_priority"] = params.u_incident_priority
        if params.u_final_severity_score:
            data["u_final_severity_score"] = params.u_final_severity_score

    # Make request
    try:
        response = requests.put(
            api_url,
            json=data,
            headers=auth_manager.get_headers(),
            timeout=config.timeout,
        )
        response.raise_for_status()

        result = response.json().get("result", {})

        return IncidentResponse(
            success=True,
            message="Incident updated successfully",
            incident_id=result.get("sys_id"),
            incident_number=result.get("number"),
        )

    except requests.RequestException as e:
        logger.error(f"Failed to update incident: {e}")
        return IncidentResponse(
            success=False,
            message=f"Failed to update incident: {str(e)}",
        )


def add_comment(
    config: ServerConfig,
    auth_manager: AuthManager,
    params: AddCommentParams,
) -> IncidentResponse:
    """
    Add a comment to an incident in ServiceNow.

    Args:
        config: Server configuration.
        auth_manager: Authentication manager.
        params: Parameters for adding the comment.

    Returns:
        Response with the result of the operation.
    """
    # Determine if incident_id is a number or sys_id
    incident_id = params.incident_id
    if len(incident_id) == 32 and all(c in "0123456789abcdef" for c in incident_id):
        # This is likely a sys_id
        api_url = f"{config.api_url}/table/incident/{incident_id}"
    else:
        # This is likely an incident number
        # First, we need to get the sys_id
        try:
            query_url = f"{config.api_url}/table/incident"
            query_params = {
                "sysparm_query": f"number={incident_id}",
                "sysparm_limit": 1,
            }

            response = requests.get(
                query_url,
                params=query_params,
                headers=auth_manager.get_headers(),
                timeout=config.timeout,
            )
            response.raise_for_status()

            result = response.json().get("result", [])
            if not result:
                return IncidentResponse(
                    success=False,
                    message=f"Incident not found: {incident_id}",
                )

            incident_id = result[0].get("sys_id")
            api_url = f"{config.api_url}/table/incident/{incident_id}"

        except requests.RequestException as e:
            logger.error(f"Failed to find incident: {e}")
            return IncidentResponse(
                success=False,
                message=f"Failed to find incident: {str(e)}",
            )

    # Build request data
    data = {}

    if params.is_work_note:
        data["work_notes"] = params.comment
    else:
        data["comments"] = params.comment

    # Make request
    try:
        response = requests.put(
            api_url,
            json=data,
            headers=auth_manager.get_headers(),
            timeout=config.timeout,
        )
        response.raise_for_status()

        result = response.json().get("result", {})

        return IncidentResponse(
            success=True,
            message="Comment added successfully",
            incident_id=result.get("sys_id"),
            incident_number=result.get("number"),
        )

    except requests.RequestException as e:
        logger.error(f"Failed to add comment: {e}")
        return IncidentResponse(
            success=False,
            message=f"Failed to add comment: {str(e)}",
        )


def resolve_incident(
    config: ServerConfig,
    auth_manager: AuthManager,
    params: ResolveIncidentParams,
) -> IncidentResponse:
    """
    Resolve an incident in ServiceNow.

    Args:
        config: Server configuration.
        auth_manager: Authentication manager.
        params: Parameters for resolving the incident.

    Returns:
        Response with the result of the operation.
    """
    # Determine if incident_id is a number or sys_id
    incident_id = params.incident_id
    if len(incident_id) == 32 and all(c in "0123456789abcdef" for c in incident_id):
        # This is likely a sys_id
        api_url = f"{config.api_url}/table/incident/{incident_id}"
    else:
        # This is likely an incident number
        # First, we need to get the sys_id
        try:
            query_url = f"{config.api_url}/table/incident"
            query_params = {
                "sysparm_query": f"number={incident_id}",
                "sysparm_limit": 1,
            }

            response = requests.get(
                query_url,
                params=query_params,
                headers=auth_manager.get_headers(),
                timeout=config.timeout,
            )
            response.raise_for_status()

            result = response.json().get("result", [])
            if not result:
                return IncidentResponse(
                    success=False,
                    message=f"Incident not found: {incident_id}",
                )

            incident_id = result[0].get("sys_id")
            api_url = f"{config.api_url}/table/incident/{incident_id}"

        except requests.RequestException as e:
            logger.error(f"Failed to find incident: {e}")
            return IncidentResponse(
                success=False,
                message=f"Failed to find incident: {str(e)}",
            )

    # Build request data
    data = {
        "state": "6",  # Resolved
        "close_code": params.resolution_code,
        "close_notes": params.resolution_notes,
        "resolved_at": "now",
    }

    # Make request
    try:
        response = requests.put(
            api_url,
            json=data,
            headers=auth_manager.get_headers(),
            timeout=config.timeout,
        )
        response.raise_for_status()

        result = response.json().get("result", {})

        return IncidentResponse(
            success=True,
            message="Incident resolved successfully",
            incident_id=result.get("sys_id"),
            incident_number=result.get("number"),
        )

    except requests.RequestException as e:
        logger.error(f"Failed to resolve incident: {e}")
        return IncidentResponse(
            success=False,
            message=f"Failed to resolve incident: {str(e)}",
        )


def list_incidents(
    config: ServerConfig,
    auth_manager: AuthManager,
    params: ListIncidentsParams,
) -> dict:
    """
    List incidents from ServiceNow.

    Args:
        config: Server configuration.
        auth_manager: Authentication manager.
        params: Parameters for listing incidents.

    Returns:
        Dictionary with list of incidents.
    """
    api_url = f"{config.api_url}/table/incident"

    # Build query parameters
    query_params = {
        "sysparm_limit": params.limit,
        "sysparm_offset": params.offset,
        "sysparm_display_value": "true",
        "sysparm_exclude_reference_link": "true",
    }
    
    # Add filters
    filters = []
    if params.state:
        filters.append(f"state={params.state}")
    if params.assigned_to:
        filters.append(f"assigned_to={params.assigned_to}")
    if params.category:
        filters.append(f"category={params.category}")
    if params.query:
        filters.append(f"short_descriptionLIKE{params.query}^ORdescriptionLIKE{params.query}")
    
    if filters:
        query_params["sysparm_query"] = "^".join(filters)
    
    # Make request
    try:
        response = requests.get(
            api_url,
            params=query_params,
            headers=auth_manager.get_headers(),
            timeout=config.timeout,
        )
        response.raise_for_status()
        
        data = response.json()
        incidents = []
        
        for incident_data in data.get("result", []):
            # Handle assigned_to field which could be a string or a dictionary
            assigned_to = incident_data.get("assigned_to")
            if isinstance(assigned_to, dict):
                assigned_to = assigned_to.get("display_value")
            
            incident = {
                "sys_id": incident_data.get("sys_id"),
                "number": incident_data.get("number"),
                "short_description": incident_data.get("short_description"),
                "description": incident_data.get("description"),
                "state": incident_data.get("state"),
                "priority": incident_data.get("priority"),
                "assigned_to": assigned_to,
                "category": incident_data.get("category"),
                "subcategory": incident_data.get("subcategory"),
                "created_on": incident_data.get("sys_created_on"),
                "updated_on": incident_data.get("sys_updated_on"),
            }
            incidents.append(incident)
        
        return {
            "success": True,
            "message": f"Found {len(incidents)} incidents",
            "incidents": incidents
        }
        
    except requests.RequestException as e:
        logger.error(f"Failed to list incidents: {e}")
        return {
            "success": False,
            "message": f"Failed to list incidents: {str(e)}",
            "incidents": []
        }


def get_incident_by_number(
    config: ServerConfig,
    auth_manager: AuthManager,
    params: GetIncidentByNumberParams,
) -> dict:
    """
    Fetch a single incident from ServiceNow by its number.

    Args:
        config: Server configuration.
        auth_manager: Authentication manager.
        params: Parameters for fetching the incident.

    Returns:
        Dictionary with the incident details.
    """
    api_url = f"{config.api_url}/table/incident"

    # Build query parameters
    query_params = {
        "sysparm_query": f"number={params.incident_number}",
        "sysparm_limit": 1,
        "sysparm_display_value": "true",
        "sysparm_exclude_reference_link": "true",
    }

    # Make request
    try:
        response = requests.get(
            api_url,
            params=query_params,
            headers=auth_manager.get_headers(),
            timeout=config.timeout,
        )
        response.raise_for_status()

        data = response.json()
        result = data.get("result", [])

        if not result:
            return {
                "success": False,
                "message": f"Incident not found: {params.incident_number}",
            }

        incident_data = result[0]
        assigned_to = incident_data.get("assigned_to")
        if isinstance(assigned_to, dict):
            assigned_to = assigned_to.get("display_value")

        incident = {
            "sys_id": incident_data.get("sys_id"),
            "number": incident_data.get("number"),
            "short_description": incident_data.get("short_description"),
            "description": incident_data.get("description"),
            "state": incident_data.get("state"),
            "priority": incident_data.get("priority"),
            "assigned_to": assigned_to,
            "category": incident_data.get("category"),
            "subcategory": incident_data.get("subcategory"),
            "created_on": incident_data.get("sys_created_on"),
            "updated_on": incident_data.get("sys_updated_on"),
        }

        return {
            "success": True,
            "message": f"Incident {params.incident_number} found",
            "incident": incident,
        }

    except requests.RequestException as e:
        logger.error(f"Failed to fetch incident: {e}")
        return {
            "success": False,
            "message": f"Failed to fetch incident: {str(e)}",
        }

"""
Utility for loading and applying custom fields from configuration.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional
import yaml

logger = logging.getLogger(__name__)


def load_custom_fields(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load custom fields configuration from YAML file.
    
    Args:
        config_path: Path to custom fields config file. 
                    Defaults to config/incident_custom_fields.yaml
    
    Returns:
        Dictionary of custom field definitions
    """
    if config_path is None:
        # Default to config/incident_custom_fields.yaml relative to project root
        project_root = Path(__file__).parent.parent.parent.parent
        config_path = project_root / "config" / "incident_custom_fields.yaml"
    else:
        config_path = Path(config_path)
    
    if not config_path.exists():
        logger.warning(f"Custom fields config not found: {config_path}")
        return {"custom_fields": []}
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            return config or {"custom_fields": []}
    except Exception as e:
        logger.error(f"Error loading custom fields config: {e}")
        return {"custom_fields": []}


def apply_custom_fields(data: Dict[str, Any], params: Any, config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Apply custom fields from params to data dictionary based on configuration.
    
    Args:
        data: The data dictionary to add fields to
        params: The params object containing field values
        config_path: Optional path to custom fields config
    
    Returns:
        Updated data dictionary with custom fields
    """
    config = load_custom_fields(config_path)
    custom_fields = config.get("custom_fields", [])
    
    for field in custom_fields:
        field_name = field.get("name")
        if field_name and hasattr(params, field_name):
            field_value = getattr(params, field_name)
            if field_value is not None:
                data[field_name] = field_value
    
    return data


def get_custom_field_definitions(config_path: Optional[str] = None) -> list:
    """
    Get list of custom field definitions for dynamic model creation.
    
    Args:
        config_path: Optional path to custom fields config
    
    Returns:
        List of field definitions
    """
    config = load_custom_fields(config_path)
    return config.get("custom_fields", [])

# Made with Bob

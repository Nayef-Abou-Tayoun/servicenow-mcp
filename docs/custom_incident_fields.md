# Custom Incident Fields Configuration

This guide explains how to add custom fields to incident creation using a configuration file approach.

## Overview

You can define custom fields in a YAML configuration file and use the provided utility to apply them automatically. This keeps your custom field definitions separate from the core code.

## Configuration File

Edit the file: `config/incident_custom_fields.yaml`

### Format

```yaml
custom_fields:
  - name: field_name
    type: string
    required: false
    description: Description of the field
```

### Example

```yaml
custom_fields:
  - name: location
    type: string
    required: false
    description: Location of the incident
  
  - name: business_service
    type: string
    required: false
    description: Business service affected
  
  - name: cmdb_ci
    type: string
    required: false
    description: Configuration item
  
  - name: u_custom_field
    type: string
    required: false
    description: Your custom ServiceNow field
```

## Using Custom Fields

### Option 1: Create a Wrapper Function (Recommended)

Create your own wrapper that uses the custom fields utility:

```python
from servicenow_mcp.tools.incident_tools import create_incident as _create_incident
from servicenow_mcp.utils.custom_fields import apply_custom_fields
from pydantic import BaseModel, Field
from typing import Optional

class CustomCreateIncidentParams(BaseModel):
    """Extended parameters with custom fields."""
    # Standard fields
    short_description: str = Field(..., description="Short description")
    description: Optional[str] = Field(None, description="Description")
    # ... other standard fields ...
    
    # Your custom fields
    location: Optional[str] = Field(None, description="Location")
    business_service: Optional[str] = Field(None, description="Business service")

def create_incident_with_custom_fields(config, auth_manager, params):
    """Create incident with custom fields support."""
    # Build base data
    data = {"short_description": params.short_description}
    
    # Add standard fields
    if params.description:
        data["description"] = params.description
    # ... add other standard fields ...
    
    # Apply custom fields from config
    data = apply_custom_fields(data, params)
    
    # Call original function with modified data
    return _create_incident(config, auth_manager, params)
```

### Option 2: Direct Modification (Simple)

If you prefer to modify `incident_tools.py` directly for your custom fields:

1. Add field to `CreateIncidentParams`:
```python
class CreateIncidentParams(BaseModel):
    # ... existing fields ...
    location: Optional[str] = Field(None, description="Location of the incident")
```

2. Add field to data dictionary in `create_incident()`:
```python
if params.location:
    data["location"] = params.location
```

## Utility Functions

The `custom_fields.py` utility provides:

- `load_custom_fields(config_path)` - Load field definitions from YAML
- `apply_custom_fields(data, params, config_path)` - Apply custom fields to data dict
- `get_custom_field_definitions(config_path)` - Get field definitions for dynamic models

## Example Usage

```python
from servicenow_mcp.utils.custom_fields import apply_custom_fields

# In your create function
data = {"short_description": "Issue"}

# Automatically add any custom fields defined in YAML
data = apply_custom_fields(data, params)

# data now includes location, business_service, etc. if they were in params
```

## Benefits

- **Separation**: Keep custom field definitions in config file
- **Flexibility**: Easy to add/remove fields by editing YAML
- **Maintainability**: No need to modify core code for each new field
- **Documentation**: YAML serves as documentation of available custom fields

## Notes

- Field names must match ServiceNow field names exactly
- Use `u_` prefix for custom fields in ServiceNow (e.g., `u_custom_field`)
- The utility only applies fields that exist in both the config and the params object
- All custom fields are optional by default
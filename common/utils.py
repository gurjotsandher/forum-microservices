def validate_tenant_id(headers):
    """
    Validate and extract the X-Tenant-ID header.
    Raise a ValueError if the header is missing.
    """
    tenant_id = headers.get("X-Tenant-ID")
    if not tenant_id:
        raise ValueError("Tenant ID is required")
    return tenant_id

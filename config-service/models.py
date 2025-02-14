from extensions import db


class TenantConfig(db.Model):
    """Stores configuration for each tenant."""
    __tablename__ = "tenant_db"

    # Primary key for this table (auto-generated by SQLAlchemy)
    id = db.Column(db.Integer, primary_key=True)

    # Tenant ID, must be unique for each tenant
    tenant_id = db.Column(db.String(100), unique=True, nullable=False)

    # Database URL for the tenant (this will be used to connect to the tenant-specific database)
    database_url = db.Column(db.String(255), nullable=False)

    # Feature flags or other configuration settings in JSON format
    feature_flags = db.Column(db.JSON, nullable=True)

    # Timestamp for when this config was created
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return f"<TenantConfig {self.tenant_id}>"

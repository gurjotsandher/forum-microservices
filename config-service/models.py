from extensions import db

class TenantConfig(db.Model):
    __tablename__ = "tenant_config"
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.String(100), unique=True, nullable=False)
    db_url = db.Column(db.String(255), nullable=False)
    feature_flags = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

"""Add password_hash field to User model

Revision ID: f3eae4ed6040
Revises: fa15c284d2a7
Create Date: 2025-02-15 00:40:17.987293

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f3eae4ed6040'
down_revision = 'fa15c284d2a7'
branch_labels = None
depends_on = None

def upgrade():
    # Step 1: Add the 'password_hash' column with NULL allowed
    op.add_column('users', sa.Column('password_hash', sa.String(length=128), nullable=True))

    # Step 2: Update existing users with password hashes (you can decide on a default value here, or leave it empty)
    # Example: Set default password hash for all existing users (replace 'default_hash' with a real value)
    op.execute("""
        UPDATE users SET password_hash = 'default_hash' WHERE password_hash IS NULL;
    """)

    # Step 3: Alter the column to NOT NULL
    op.alter_column('users', 'password_hash', nullable=False)

def downgrade():
    # Revert the changes
    op.drop_column('users', 'password_hash')

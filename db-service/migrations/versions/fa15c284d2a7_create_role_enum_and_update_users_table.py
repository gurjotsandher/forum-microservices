"""Create role ENUM and update users table

Revision ID: fa15c284d2a7
Revises: 
Create Date: 2025-02-14 23:00:16.688884

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fa15c284d2a7'
down_revision = None
branch_labels = None
depends_on = None
def upgrade():
    # Create the 'role' ENUM type if it doesn't exist
    op.execute("""
    DO $$
    BEGIN
        -- Check if the role ENUM type already exists, if not, create it
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'role') THEN
            CREATE TYPE role AS ENUM ('user', 'mod', 'admin', 'guest');
        END IF;
    END;
    $$;
    """)

    # First, set the default value to a valid ENUM type (not the string 'user')
    op.execute("""
    ALTER TABLE users ALTER COLUMN role SET DEFAULT 'user'::role;
    """)

    # Alter the 'role' column in 'users' table to use the 'role' ENUM type
    op.alter_column(
        'users', 'role',
        existing_type=sa.VARCHAR(length=50),
        type_=sa.Enum('user', 'mod', 'admin', 'guest', name='role'),
        existing_nullable=False,
        postgresql_using="role::text::role"  # Ensure existing data is cast to the new ENUM type
    )

    # Drop the 'password_hash' column if it's no longer needed
    op.drop_column('users', 'password_hash')

    # Create the boards table
    op.create_table(
        'boards',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=80), nullable=False),
        sa.Column('description', sa.String(length=256), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create the threads table
    op.create_table(
        'threads',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('board_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=128), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(('board_id',), ('boards.id',)),  # ForeignKey for board_id
        sa.PrimaryKeyConstraint('id')
    )

    # Create the posts table
    op.create_table(
        'posts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('thread_id', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(('thread_id',), ('threads.id',)),  # ForeignKey for thread_id
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    # Add back the 'password_hash' column if needed
    op.add_column('users', sa.Column('password_hash', sa.VARCHAR(length=128), nullable=False))

    # Revert the 'role' column back to its original type (VARCHAR)
    op.alter_column(
        'users', 'role',
        existing_type=sa.Enum('user', 'mod', 'admin', 'guest', name='role'),
        type_=sa.VARCHAR(length=50),
        existing_nullable=False,
        existing_server_default=sa.text("'user'::character varying")
    )

    # Drop the boards, threads, and posts tables
    op.drop_table('posts')
    op.drop_table('threads')
    op.drop_table('boards')

    # Drop the 'role' ENUM type
    op.execute("DROP TYPE IF EXISTS role")

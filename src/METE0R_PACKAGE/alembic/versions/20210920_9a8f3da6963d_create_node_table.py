"""Create node table

Revision ID: 9a8f3da6963d
Revises:
Create Date: 2021-09-20 10:57:40.982541

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "9a8f3da6963d"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    node_table = op.create_table(
        "node",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.Unicode(length=100), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(
            ["parent_id"], ["node.id"], name=op.f("fk_node_parent_id_node")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_node")),
        sa.UniqueConstraint(
            "parent_id", "name", name=op.f("uq_node_parent_id")
        ),
    )
    op.create_index(
        op.f("ix_node_parent_id"), "node", ["parent_id"], unique=False
    )
    op.bulk_insert(
        node_table,
        [
            {"name": "", "content": "Welcome!"},
        ],
    )


def downgrade():
    op.drop_index(op.f("ix_node_parent_id"), table_name="node")
    op.drop_table("node")

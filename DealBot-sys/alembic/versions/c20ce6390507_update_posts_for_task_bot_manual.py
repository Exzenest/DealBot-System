from alembic import op
import sqlalchemy as sa


revision = "c20ce6390507"
down_revision = "079575287daf"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("posts") as batch_op:
        batch_op.add_column(sa.Column("subject", sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column("file_id", sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column("file_name", sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True))
        batch_op.alter_column("executor_id", existing_type=sa.BigInteger(), nullable=True)
        batch_op.alter_column("channel_message_id", existing_type=sa.BigInteger(), nullable=True)

    op.execute("UPDATE posts SET subject = category WHERE subject IS NULL")
    op.execute("UPDATE posts SET updated_at = created_at WHERE updated_at IS NULL")

    with op.batch_alter_table("posts") as batch_op:
        batch_op.alter_column("subject", existing_type=sa.String(length=255), nullable=False)


def downgrade() -> None:
    with op.batch_alter_table("posts") as batch_op:
        batch_op.drop_column("updated_at")
        batch_op.drop_column("file_name")
        batch_op.drop_column("file_id")
        batch_op.drop_column("subject")
"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""

import sqlalchemy as sa
from alembic import op
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


_ENUMS=[]


def upgrade() -> None:
    for _ENUM in _ENUMS:
        _ENUM.create(op.get_bind(), checkfirst=True)
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
    for _ENUM in _ENUMS:
        _ENUM.drop(op.get_bind(), checkfirst=True)

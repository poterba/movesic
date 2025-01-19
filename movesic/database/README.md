# DATABASE

There is specific action about Alembic and enums: to make everyone happy you should wrap them in model

```python
class ENUM(enum.Enum):
    A = 0
    B = 1
    C = 2

_ENUM: sa.Enum = sa.Enum(
    ACTION_TYPE,
    name="_enum",
    create_constraint=True,
    metadata=Base.metadata,
    validate_strings=True,
)
```

and (unfortunately, manually) fix their generic creation in migrations afterwards:

```python
def upgrade() -> None:
    _ENUM.create(op.get_bind(), checkfirst=True)
    # ...
    op.create_table('example',
        sa.Column('enum', _ENUM, nullable=False),
    )

def downgrade() -> None:
    # ...
    _ENUM.drop(op.get_bind(), checkfirst=True)
```

Fortunately, I've already included this approach into [`mako template`](migrations/script.py.mako), so all you have to do is add new enums to `_ENUMS` list.
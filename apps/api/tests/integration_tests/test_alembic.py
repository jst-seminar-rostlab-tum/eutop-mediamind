import subprocess


def test_no_divergent_alembic_heads():
    """Check that there are no divergent alembic heads in the migrations."""
    result = subprocess.run(
        ["alembic", "heads"], capture_output=True, text=True
    )
    # If there are multiple heads, alembic will print more than one head
    heads = [line for line in result.stdout.splitlines() if "(head)" in line]
    assert len(heads) <= 1, (
        f"There are divergent alembic heads! {len(heads)} found. "
        "Run `alembic merge` to fix."
    )

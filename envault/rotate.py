"""Password rotation for envault vaults."""

from typing import Optional
from envault.vault import load_vault, save_vault
from envault.audit import record_event


class RotationError(Exception):
    """Raised when vault password rotation fails."""
    pass


def rotate_password(
    project_dir: str,
    old_password: str,
    new_password: str,
    confirm_password: Optional[str] = None,
) -> int:
    """Re-encrypt all vault secrets under a new password.

    Args:
        project_dir: Path to the project whose vault should be rotated.
        old_password: Current vault password (used to decrypt).
        new_password: New password to encrypt the vault under.
        confirm_password: Optional confirmation of new_password; must match
                          new_password when provided.

    Returns:
        Number of variables re-encrypted.

    Raises:
        RotationError: If passwords don't match or old password is wrong.
    """
    if confirm_password is not None and new_password != confirm_password:
        raise RotationError("New password and confirmation do not match.")

    if old_password == new_password:
        raise RotationError(
            "New password must be different from the current password."
        )

    # load_vault raises ValueError / FileNotFoundError on bad password / missing file
    try:
        secrets = load_vault(project_dir, old_password)
    except (ValueError, FileNotFoundError) as exc:
        raise RotationError(f"Could not open vault with old password: {exc}") from exc

    save_vault(project_dir, secrets, new_password)

    count = len(secrets)
    record_event(
        project_dir,
        "rotate",
        {"variables_rotated": count},
    )
    return count

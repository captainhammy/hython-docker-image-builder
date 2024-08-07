"""Docker related functions."""

# Standard Library
import subprocess


def build_full_tag_name(tag_base: str, version: str) -> str:
    """Build a full image tag name.

    Args:
        tag_base: The user/repo portion of the tag name.
        version: The image version.

    Returns:
        The combined image tag name.
    """
    return f"{tag_base}:{version}"


def check_tag_exists(tag_base: str, version: str) -> bool:
    """Check of a tag of name:version already exists in dockerhub.

    Args:
        tag_base: TThe user/repo portion of the tag name.
        version: The version to check.

    Returns:
        Whether a matching tag exists.
    """
    tag_name = build_full_tag_name(tag_base, version)

    print(f"Checking if tag {tag_name} exists")

    try:
        subprocess.run(["docker", "manifest", "inspect", tag_name], capture_output=True, check=True)

    except subprocess.CalledProcessError:
        return False

    return True

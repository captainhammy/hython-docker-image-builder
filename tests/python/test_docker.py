"""Test the houdini_docker_builder.docker module."""

# Standard Library
import subprocess

# Third Party
import pytest

# houdini_docker_builder
from houdini_docker_builder import docker


def test_build_full_tag_name():
    """Test houdini_docker_builder.docker.build_full_tag_name()."""
    result = docker.build_full_tag_name("name/repo", "20.0")
    assert result == "name/repo:20.0"


@pytest.mark.parametrize("exists", (False, True))
def test_check_tag_exists(mocker, fp, exists):
    """Test houdini_docker_builder.docker.check_tag_exists()."""
    mock_build_name = mocker.patch("houdini_docker_builder.docker.build_full_tag_name")

    def callback_function(*args, **kwargs):
        if not exists:
            raise subprocess.CalledProcessError(1, "msg")

    fp.register(
        ["docker", "manifest", "inspect", mock_build_name.return_value],
        callback=callback_function,
    )

    result = docker.check_tag_exists("name", "version")

    assert result == exists

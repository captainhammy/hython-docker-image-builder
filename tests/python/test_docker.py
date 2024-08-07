"""Test the hython_docker_image_builder.docker module."""

# Standard Library
import subprocess

# Third Party
import pytest

# hython_docker_image_builder
from hython_docker_image_builder import docker


def test_build_full_tag_name():
    """Test hython_docker_image_builder.docker.build_full_tag_name()."""
    result = docker.build_full_tag_name("name/repo", "20.0")
    assert result == "name/repo:20.0"


@pytest.mark.parametrize("exists", (False, True))
def test_check_tag_exists(mocker, fp, exists):
    """Test hython_docker_image_builder.docker.check_tag_exists()."""
    mock_build_name = mocker.patch("hython_docker_image_builder.docker.build_full_tag_name")

    def callback_function(*args, **kwargs):
        if not exists:
            raise subprocess.CalledProcessError(1, "msg")

    fp.register(
        ["docker", "manifest", "inspect", mock_build_name.return_value],
        callback=callback_function,
    )

    result = docker.check_tag_exists("name", "version")

    assert result == exists

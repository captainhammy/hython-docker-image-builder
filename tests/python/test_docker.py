"""Test the hython_docker_image_builder.docker module."""

# Future
from __future__ import annotations

# Standard Library
import subprocess
from typing import TYPE_CHECKING

# Third Party
import pytest

# hython_docker_image_builder
from hython_docker_image_builder import docker

if TYPE_CHECKING:
    from pytest_mock import MockerFixture
    from pytest_subprocess.fake_process import FakeProcess


def test_build_full_tag_name() -> None:
    """Test hython_docker_image_builder.docker.build_full_tag_name()."""
    result = docker.build_full_tag_name("name/repo", "20.0")
    assert result == "name/repo:20.0"


@pytest.mark.parametrize("exists", (False, True))
def test_check_tag_exists(mocker: MockerFixture, fp: FakeProcess, exists: bool) -> None:
    """Test hython_docker_image_builder.docker.check_tag_exists()."""
    mock_build_name = mocker.patch("hython_docker_image_builder.docker.build_full_tag_name")

    def callback_function(*args, **kwargs):  # ruff:ignore[missing-type-args, missing-type-kwargs, missing-return-type-private-function]
        if not exists:
            raise subprocess.CalledProcessError(1, "msg")

    fp.register(
        ["docker", "manifest", "inspect", mock_build_name.return_value],
        callback=callback_function,
    )

    result = docker.check_tag_exists("name", "version")

    assert result == exists

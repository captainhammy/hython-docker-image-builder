"""Test the hython_docker_image_builder.build module."""

# Standard Library
import contextlib
import http
import pathlib

# Third Party
import pytest

# hython_docker_image_builder
import sidefx
from hython_docker_image_builder import builder

# Tests


@pytest.mark.parametrize(
    "build,expected,",
    (
        ("123", None),
        (None, "789"),
        ("321", "321"),
    ),
)
def test__determine_release(build, expected):
    """Test hython_docker_image_builder.build._determine_release()."""
    releases = [
        {"build": "456", "date": "2024/10/26", "version": "20.0"},
        {"build": "789", "date": "2024/10/27", "version": "19.5"},
        {"build": "321", "date": "2024/09/27", "version": "19.0"},
    ]

    raiser = pytest.raises(RuntimeError) if expected is None else contextlib.nullcontext()

    with raiser:
        result = builder._determine_release(releases, build)

        assert result["build"] == expected


@pytest.mark.parametrize(
    "version_str,expected, raiser",
    (
        ("20", (None, None), pytest.raises(RuntimeError)),
        ("20.0", ("20.0", None), contextlib.nullcontext()),
        ("20.0.123", ("20.0", "123"), contextlib.nullcontext()),
        ("20.0.123.4", ("20.0", "123.4"), contextlib.nullcontext()),
        ("", (None, None), contextlib.nullcontext()),
    ),
)
def test__determine_version_info(version_str, expected, raiser):
    """Test hython_docker_image_builder.build._determine_version_info()."""
    with raiser:
        result = builder._determine_version_info(version_str)

        assert result == expected


@pytest.mark.parametrize("has_error", (False, True))
def test__download_file(mocker, has_error):
    """Test hython_docker_image_builder.build._download_file()."""
    mock_url = mocker.MagicMock(spec=str)
    mock_target = mocker.MagicMock(spec=pathlib.Path)

    mock_copy = mocker.patch("shutil.copyfileobj")

    mock_get = mocker.patch("requests.get")
    mock_get.return_value.status_code = http.HTTPStatus.OK if not has_error else http.HTTPStatus.BAD_REQUEST

    raiser = pytest.raises(RuntimeError) if has_error else contextlib.nullcontext()

    with raiser:
        builder._download_file(mock_url, mock_target)

        mock_copy.assert_called_with(mock_get.return_value.raw, mock_target.open.return_value.__enter__.return_value)

    mock_get.assert_called_with(mock_url, stream=True)


def test__download_product(mocker):
    """Test hython_docker_image_builder.build._download_product()."""
    build = {
        "download_url": "https://some/url",
        "filename": "houdini-20.0.724-linux_x86_64_gcc11.2.tar.gz",
        "hash": "b9968530277a07bb50ce0690c0c5bbcd",
    }

    mock_service = mocker.patch("hython_docker_image_builder.builder.sidefx.service")
    mock_service.download.get_daily_build_download.return_value = build

    mock_download = mocker.patch("hython_docker_image_builder.builder._download_file")
    mock_verify = mocker.patch("hython_docker_image_builder.builder._verify_checksum")

    release = {"version": "20.0", "build": "724"}

    mock_target = mocker.MagicMock(spec=pathlib.Path)
    result = builder._download_product(mock_service, release, "houdini", mock_target)

    assert result == mock_target / build["filename"]

    mock_service.download.get_daily_build_download.assert_called_with(
        product="houdini",
        version="20.0",
        build="724",
        platform="linux",
    )
    mock_download.assert_called_with(build["download_url"], mock_target / build["filename"])
    mock_verify.assert_called_with(mock_target / build["filename"], build["hash"])


@pytest.mark.parametrize(
    "has_releases,has_build",
    (
        (False, False),
        (True, False),
        (True, True),
    ),
)
def test__get_target_release(mocker, has_releases, has_build):
    """Test hython_docker_image_builder.build._get_target_release()."""
    mock_releases = [mocker.MagicMock(spec=dict)] if has_releases else []

    mock_service = mocker.MagicMock()
    mock_service.download.get_daily_builds_list.return_value = mock_releases

    mock_version = mocker.MagicMock(spec=str)

    mock_major_minor = mocker.MagicMock(spec=str)
    build = "123" if has_build else None

    mocker.patch("hython_docker_image_builder.builder._determine_version_info", return_value=(mock_major_minor, build))

    mock_get_release = mocker.patch("hython_docker_image_builder.builder._determine_release")

    raiser = contextlib.nullcontext() if has_releases else pytest.raises(RuntimeError)

    with raiser:
        result = builder._get_target_release(mock_service, mock_version)

        assert result == mock_get_release.return_value

        mock_service.download.get_daily_builds_list.assert_called_with(
            product="houdini", version=mock_major_minor, platform="linux", only_production=not has_build
        )


def test__verify_checksum(shared_datadir):
    """Test hython_docker_image_builder.build._verify_checksum()."""
    with pytest.raises(RuntimeError):
        builder._verify_checksum(shared_datadir / "verify_checksum.txt", "000")

    builder._verify_checksum(shared_datadir / "verify_checksum.txt", "b856d9b6874bd71d9f8ecae91df5e423")


@pytest.mark.parametrize(
    "version,tag_exists,force,unsupported",
    (
        ("20.0", True, False, False),
        ("19.5", True, True, False),
        ("19.0", False, False, True),
        ("20.0", False, False, False),
    ),
)
def test_check_build_can_be_installed(mocker, version, tag_exists, force, unsupported):
    """Test hython_docker_image_builder.build.check_build_can_be_installed()."""
    mock_service = mocker.MagicMock(spec=sidefx._Service)

    mocker.patch(
        "hython_docker_image_builder.builder._get_target_release", return_value={"version": version, "build": "724"}
    )

    mocker.patch("hython_docker_image_builder.builder.docker.check_tag_exists", return_value=tag_exists)
    mocker.patch("hython_docker_image_builder.builder.docker.build_full_tag_name")

    mock_download = mocker.patch("hython_docker_image_builder.builder._download_product")

    mock_launcher = mocker.MagicMock(spec=pathlib.Path)
    mock_archive = mocker.MagicMock(spec=pathlib.Path)
    mock_download.side_effect = (mock_launcher, mock_archive)

    raiser = pytest.raises(RuntimeError) if unsupported else contextlib.nullcontext()

    with raiser:
        result = builder.check_build_can_be_installed(mock_service, version, "name/repo", force=force)

        if tag_exists and not force:
            assert result == {}

        else:
            assert result == {
                "version": version,
                "build": "724",
                "launcher_name": mock_launcher.name,
                "iso_name": mock_archive.name,
            }


def test__get_service(mocker):
    """Test hython_docker_image_builder.build.get_service()."""
    mock_service = mocker.patch("hython_docker_image_builder.builder.sidefx.service")

    mock_id = mocker.MagicMock(spec=str)
    mock_secret = mocker.MagicMock(spec=str)

    result = builder.get_service(mock_id, mock_secret)

    assert result == mock_service.return_value

    mock_service.assert_called_with(
        access_token_url=builder.TOKEN_URL,
        client_id=mock_id,
        client_secret_key=mock_secret,
        endpoint_url=builder.ENDPOINT_URL,
    )

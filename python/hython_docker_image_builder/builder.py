"""Builder related functions."""

# Future
from __future__ import annotations

# Standard Library
import hashlib
import pathlib
import shutil
from http import HTTPStatus
from operator import itemgetter

# Third Party
import requests

# hython_docker_image_builder
import sidefx  # type: ignore
from hython_docker_image_builder import docker

TOKEN_URL = "https://www.sidefx.com/oauth2/application_token"
ENDPOINT_URL = "https://www.sidefx.com/api/"

SUPPORTED_MAJOR_MINOR_VERSIONS = ("19.5", "20.0", "20.5", "21.0")

# Non-Public Functions


def _determine_version_info(version_arg: str) -> tuple[str | None, str | None]:
    """Determine the target version information.

    `version_arg` can be empty, a {major.minor} or {major.minor.build} type string.

    Args:
        version_arg: A version string to use in determining which version to install.

    Returns:
        The target {major.minor} version and build number, if any
    """
    if version_arg:
        components = version_arg.split(".")

        if len(components) < 2:  # noqa: PLR2004
            raise RuntimeError(f"Invalid version argument: {version_arg} must have at least 2 components")

        major_minor = ".".join(components[:2])
        build = ".".join(components[2:]) if len(components) > 2 else None  # noqa: PLR2004

    else:
        major_minor = None
        build = None

    return major_minor, build


def _download_file(url: str, target: pathlib.Path) -> None:
    """Save the url to the target file.

    Args:
        url: The url to download.
        target: The path to save the file as.

    Raises:
        RuntimeError: If the url could not be grabbed.
    """
    r = requests.get(url, stream=True)

    if r.status_code == HTTPStatus.OK:
        with target.open("wb") as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)
    else:
        raise RuntimeError(f"Error downloading file. Returned code {r.status_code}")


def _download_product(
    service: sidefx._Service, release: dict, product: str, target_folder: pathlib.Path
) -> pathlib.Path:
    """Download the desired product.

    Args:
        service: The SideFX Web API connection.
        release: The build information dictionary.
        product: The product name to download.
        target_folder: The folder to save the downloaded product.

    Returns:
        The downloaded file path.
    """
    product_info = service.download.get_daily_build_download(
        product=product,
        version=release["version"],
        build=release["build"],
        platform="linux",
    )

    target = target_folder / product_info["filename"]

    _download_file(product_info["download_url"], target)

    print(f"Downloaded file: {target.resolve().as_posix()}")

    # Verify the file checksum is matching
    _verify_checksum(target, product_info["hash"])

    return target


def _determine_release(releases: list[dict], build: str | None) -> dict:
    if build is not None:
        # Check all the releases for one that matches the target build.
        for release in releases:
            if release["build"] == build:
                release_to_install = release
                break

        # If one isn't found, then raise an exception.
        else:
            raise RuntimeError(f"Build {release['version']}.{build} not found!")

    else:
        # Sort the releases by date to actually get the latest production build.
        # Without doing this, a new build of an older version (e.g. 19.5) would
        # not be found if any build of a newer version (e.g. 20.0) existed.
        releases.sort(key=itemgetter("date"))

        release_to_install = releases[-1]

    return release_to_install


def _get_target_release(service: sidefx._Service, version_arg: str) -> dict:
    """Get the target release to install.

    `version_arg` can be empty, a {major.minor} or {major.minor.build} type
    string. If the value is empty, the most recent production build is chosen.
    If it is a {major.minor}, then that is used to find the latest production build of
    that release.

    Args:
        service: The SideFX Web API connection.
        version_arg: A version string to use in determining which version to install.

    Returns:
        The target release dictionary.

    Raises:
        RuntimeError: No matching version could be found to install.
    """
    major_minor, build = _determine_version_info(version_arg)

    releases_list = service.download.get_daily_builds_list(
        product="houdini",
        version=major_minor,
        platform="linux",
        # If no specific build was set, we'll ask for a matching Production build.
        only_production=not bool(build),
    )

    if not releases_list:
        raise RuntimeError(f"No releases matching {major_minor} could be found.")

    return _determine_release(releases_list, build)


def _verify_checksum(file_path: pathlib.Path, expected_hash: str) -> None:
    """Verify the file hash matches the expected value.

    Args:
        file_path: The file to check.
        expected_hash: The expected md5 hash.

    Raises:
        RuntimeError: If the file hash does not match the expected value.
    """
    with file_path.open("rb") as handle:
        digest = hashlib.file_digest(handle, "md5")

    if digest.hexdigest() != expected_hash:
        raise RuntimeError(f"Checksum for {file_path.name} does not match!")


# Functions


def check_build_can_be_installed(service: sidefx._Service, version_arg: str, tag_base: str, *, force: bool) -> dict:
    """Check whether a build can be installed.

    Args:
        service: The SideFX Web API connection.
        version_arg: A version string to use in determining which version to install.
        tag_base: The dockerhub user/repo name.
        force: Whether to force building if the target tag already exists.

    Returns:
        A dictionary containing information about the build to be installed.

    Raises:
        RuntimeError: Raised if the requested {major.minor} version is not supported.
    """
    target_release = _get_target_release(service, version_arg)

    version = target_release["version"]

    if version not in SUPPORTED_MAJOR_MINOR_VERSIONS:
        raise RuntimeError(f"Major version {version} is not supported.")

    # Create the 'full' version here since the passed in version could be something like
    # "20.0" and the resolved actual version is provided by the returned value.
    full_version = f"{version}.{target_release['build']}"

    tag_exists = docker.check_tag_exists(tag_base, full_version)

    if tag_exists and not force:
        print(f"{docker.build_full_tag_name(tag_base, full_version)} already exists, skipping")
        return {}

    # The folder the actual build files are/will be placed under. This is the major.minor portion
    # of the version to install.
    build_folder = pathlib.Path.cwd() / "dockerfiles" / version

    if not build_folder.is_dir():
        raise RuntimeError(f"Cannot find dockerfiles for {version}")

    launcher = _download_product(service, target_release, "houdini-launcher", build_folder)
    archive = _download_product(service, target_release, "launcher-iso", build_folder)

    return {
        "version": version,
        "build": target_release["build"],
        "launcher_name": launcher.name,
        "iso_name": archive.name,
    }


def get_service(client_id: str, client_secret: str) -> sidefx._Service:
    """Get a connection to the SideFX Web API.

    Args:
        client_id: The API client ID.
        client_secret: The API client secret.

    Returns:
        A connection to the SideFX Web API.
    """
    return sidefx.service(  # type: ignore
        access_token_url=TOKEN_URL,
        client_id=client_id,
        client_secret_key=client_secret,
        endpoint_url=ENDPOINT_URL,
    )

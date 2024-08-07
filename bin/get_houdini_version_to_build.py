"""Determine the houdini version to build."""

# Standard Library
import argparse
import os
import pathlib

# houdini_docker_builder
from houdini_docker_builder import builder


def build_parser() -> argparse.ArgumentParser:
    """Build the program argument parser.

    Returns:
        An argument parser.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("version")
    parser.add_argument("tag")
    parser.add_argument("client_id")
    parser.add_argument("client_secret")
    parser.add_argument("--force", action="store_true")

    return parser


def main() -> None:
    """Execute the main program."""
    parser = build_parser()

    args = parser.parse_args()
    version = args.version
    tag_base = args.tag
    client_id = args.client_id
    client_secret = args.client_secret
    force = args.force

    service = builder.get_service(client_id, client_secret)

    result = builder.check_build_can_be_installed(service, version, tag_base, force=force)

    if result:
        output_path = pathlib.Path(os.environ["GITHUB_OUTPUT"])

        with output_path.open("a", encoding="utf-8") as fp:
            fp.write(f"build_version={result['version']}\n")
            fp.write(f"build_full_version={result['version']}.{result['build']}\n")
            fp.write(f"houdini_launcher_filename={result['launcher_name']}\n")
            fp.write(f"houdini_iso_filename={result['iso_name']}\n")


if __name__ == "__main__":
    main()

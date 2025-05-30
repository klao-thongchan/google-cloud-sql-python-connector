"""
Copyright 2019 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from __future__ import absolute_import

import os

import nox

LINT_PATHS = ["google", "tests", "noxfile.py"]

TEST_PYTHON_VERSIONS = ["3.9", "3.10", "3.11", "3.12", "3.13"]


@nox.session
def lint(session):
    """Run linters.
    Returns a failure if the linters find linting errors or sufficiently
    serious code quality issues.
    """
    session.install("-r", "requirements.txt")
    session.install(
        "ruff",
        "mypy",
        "twine",
        "build",
        "importlib_metadata==7.2.1",
    )
    session.run(
        "ruff",
        "check",
        *LINT_PATHS, 
    )
    session.run(
        "mypy",
        "-p",
        "google",
        "--install-types",
        "--non-interactive",
        "--show-traceback",
    )
    # verify that pyproject.toml is valid
    session.run("python", "-m", "build", "--sdist")
    session.run("twine", "check", "--strict", "dist/*")

@nox.session()
def format(session):
    """
    Run Ruff to automatically format code.
    """
    session.install("ruff")
    session.run(
        "ruff",
        "check",
        "--fix",  
        *LINT_PATHS,
    )


def default(session, path):
    # Install all test dependencies, then install this package in-place.
    session.install("-r", "requirements-test.txt")
    session.install("-e", ".")
    session.install("-r", "requirements.txt")
    # Run py.test against the unit tests.
    session.run(
        "pytest",
        "--cov=google.cloud.sql.connector",
        "-v",
        "--cov-config=.coveragerc",
        "--cov-report=",
        "--cov-fail-under=0",
        "--junitxml=sponge_log.xml",
        path,
        *session.posargs,
    )


@nox.session(python=TEST_PYTHON_VERSIONS)
def unit(session):
    default(session, os.path.join("tests", "unit"))


@nox.session(python=TEST_PYTHON_VERSIONS)
def system(session):
    default(session, os.path.join("tests", "system"))


@nox.session(python=TEST_PYTHON_VERSIONS)
def test(session):
    default(session, os.path.join("tests", "unit"))
    default(session, os.path.join("tests", "system"))

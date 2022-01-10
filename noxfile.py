"""
Current issues:

"""
# pylint: disable=missing-function-docstring, line-too-long
import nox


nox.options.sessions = (
    "install",  # this is mandatory to ensure, that all needed modules are installed by poetry first
    "black",
    "flake8",
    "pylint",
    "mypy",
    "pytype",
    "safety",
    "pytest",
    "coverage",
)
locations = "csv_labeler", "tests", "noxfile.py"


@nox.session(python=False)
def install(session):
    session.run("poetry", "install")


@nox.session(python=False)
def black(session):
    args = session.posargs or locations
    session.run("black", "--experimental-string-processing", *args)


@nox.session(python=False)
def flake8(session):
    args = session.posargs or locations
    session.run("flake8", "--docstring-convention=numpy", *args)


@nox.session(python=False)
def pylint(session):
    args = session.posargs or locations
    session.run("pylint", "--output-format=text", *args)


@nox.session(python=False)
def pylint_code_climate(session):
    args = session.posargs or locations
    session.run(
        "pylint",
        "--exit-zero",
        "--output-format=pylint_gitlab.GitlabCodeClimateReporter",
        *args
    )


@nox.session(python=False)
def pylint_pages(session):
    args = session.posargs or locations
    session.run(
        "pylint",
        "--exit-zero",
        "--output-format=pylint_gitlab.GitlabPagesHtmlReporter",
        *args
    )


@nox.session(python=False)
def mypy(session):
    args = session.posargs or locations
    session.run("mypy", *args)


@nox.session(python=False)
def pytype(session):
    session.run("pytype", "--config=pytype.cfg", "csv_labeler")


@nox.session(python=False)
def safety(session):
    session.run(
        "poetry",
        "export",
        "--dev",
        "--format=requirements.txt",
        "--without-hashes",
        "--output=requirements.txt",
        external=True,
    )
    session.run("safety", "check", "--file=requirements.txt", "--full-report")


@nox.session(python=False)
def pytest(session):
    session.run(
        "pytest",
        "--timeout=15",
        "--capture=sys",
        "--junitxml=pytest-report.xml",
        "--cov=csv_labeler",
        "--cov-fail-under=36",
        "tests/",
    )  # in order to see output to stdout set: --capture=tee-sys


@nox.session(python=False)
def coverage(session):
    session.run("coverage", "xml")


@nox.session(python=False)
def pytest_o(session):
    session.run(
        "pytest",
        "--capture=tee-sys",
        "tests/",
    )


@nox.session(python=False)
def pytest_integration(session):
    session.run(
        "pytest",
        "--timeout=15",
        "--capture=sys",
        "tests/integration/",
    )  # in order to see output to stdout set: --capture=tee-sys

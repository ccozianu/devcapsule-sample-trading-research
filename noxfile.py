import nox

nox.options.default_venv_backend = "venv"
nox.options.sessions = ["tests", "compile", "lint"]


@nox.session(python="3.12")
def tests(session: nox.Session) -> None:
    """Run the dependency-free unit test suite against an installed package."""
    session.install(".")
    session.run("python", "-m", "unittest", "discover", "-s", "tests", "-v")


@nox.session(python="3.12", reuse_venv=True)
def compile(session: nox.Session) -> None:
    """Compile project and test modules to catch syntax errors."""
    session.run("python", "-m", "compileall", "-q", "src", "tests")


@nox.session(python="3.12")
def lint(session: nox.Session) -> None:
    """Run Ruff over source, tests, and automation code."""
    session.install("ruff>=0.6")
    session.run("ruff", "check", "src", "tests", "noxfile.py")


@nox.session(python="3.12")
def build(session: nox.Session) -> None:
    """Build the wheel and source distribution through the PEP 517 backend."""
    session.install("build>=1.2.2")
    session.run("python", "-m", "build")

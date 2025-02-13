import nox
from nox.sessions import Session

sessions = ["format", "lint", "types", "test", "safety"]

locations = "src", "tests"


@nox.session
def format(session: Session) -> None:
    args = session.posargs or locations
    session.install("---")
    session.run("", *args)

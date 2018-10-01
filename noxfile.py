import nox


@nox.session
def lint(session):
    session.install('flake8')
    session.run('flake8', 'buzz')


@nox.session(python=['3.4', '3.5', '3.6'])
def test(session):
    session.install('-e', '.[test]')
    session.run('py.test', 'tests')

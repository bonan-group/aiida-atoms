"""pytest fixtures for simplified testing."""

pytest_plugins = ["aiida.manage.tests.pytest_fixtures"]


# @pytest.fixture(scope="function", autouse=True)
# def clear_database_auto(clear_database):  # pylint: disable=unused-argument
#     """Automatically clear database in between tests."""

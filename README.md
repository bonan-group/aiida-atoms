[![Build Status][ci-badge]][ci-link]
[![Coverage Status][cov-badge]][cov-link]
[![Docs status][docs-badge]][docs-link]
[![PyPI version][pypi-badge]][pypi-link]

# aiida-atoms

AiiDA Plugin for keeping track of structure manipulations of an `ase.Atoms` objects.
Every operation acted through the `AtomsTracker` object will be recorded on the provenance graph.

## Repository contents

* [`.github/`](.github/): [Github Actions](https://github.com/features/actions) configuration
  * [`ci.yml`](.github/workflows/ci.yml): runs tests, checks test coverage and builds documentation at every new commit
  * [`publish-on-pypi.yml`](.github/workflows/publish-on-pypi.yml): automatically deploy git tags to PyPI - just generate a [PyPI API token](https://pypi.org/help/#apitoken) for your PyPI account and add it to the `pypi_token` secret of your github repository
* [`aiida_atoms/`](aiida_atoms/): The main source code of the plugin package
* [`docs/`](docs/): A documentation template ready for publication on [Read the Docs](http://aiida-diff.readthedocs.io/en/latest/)
* [`examples/`](examples/): An example of how to submit a calculation using this plugin
* [`tests/`](tests/): Basic regression tests using the [pytest](https://docs.pytest.org/en/latest/) framework (submitting a calculation, ...). Install `pip install -e .[testing]` and run `pytest`.
* [`.gitignore`](.gitignore): Telling git which files to ignore
* [`.pre-commit-config.yaml`](.pre-commit-config.yaml): Configuration of [pre-commit hooks](https://pre-commit.com/) that sanitize coding style and check for syntax errors. Enable via `pip install -e .[pre-commit] && pre-commit install`
* [`LICENSE`](LICENSE): License for your plugin
* [`README.md`](README.md): This file
* [`conftest.py`](conftest.py): Configuration of fixtures for [pytest](https://docs.pytest.org/en/latest/)
* [`pyproject.toml`](setup.json): Python package metadata for registration on [PyPI](https://pypi.org/) and the [AiiDA plugin registry](https://aiidateam.github.io/aiida-registry/) (including entry points)


## Features

- Automatic tracking of changes made to `ase.Atoms` object through its methods, and saving them to the provenance graph.
- Wrapped other common routines that records provenance for tracking.
- Provenance graph visualization.

## Installation

```shell
pip install aiida-atoms
```


## Usage


## Development

```shell
git clone https://github.com/zhubonan/aiida-atoms .
cd aiida-atoms
pip install --upgrade pip
pip install -e .[pre-commit,testing]  # install extra dependencies
pre-commit install  # install pre-commit hooks
pytest -v  # discover and run all tests
```


## License

MIT
## Contact

zhubonan@outlook.com


[ci-badge]: https://github.com/zhubonan/aiida-atoms/workflows/ci/badge.svg?branch=master
[ci-link]: https://github.com/zhubonan/aiida-atoms/actions
[cov-badge]: https://coveralls.io/repos/github/zhubonan/aiida-atoms/badge.svg?branch=master
[cov-link]: https://coveralls.io/github/zhubonan/aiida-atoms?branch=master
[docs-link]: https://zhubonan.github.io/aiida-atoms/
[docs-badge]: https://github.com/zhubonan/aiida-atoms/actions/workflows/docs.yml/badge.svg
[pypi-badge]: https://badge.fury.io/py/aiida-atoms.svg
[pypi-link]: https://badge.fury.io/py/aiida-atoms

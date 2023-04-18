# Developer guide

## Running the tests

The following will discover and run all unit test:

```
pip install --upgrade pip
pip install -e .[testing]
pytest -v
```

You can also run the tests in a virtual environment with [tox](https://tox.wiki/en/latest/):

```
pip install tox tox-conda
tox -e py38 -- -v
```

## Automatic coding style checks

Enable enable automatic checks of code sanity and coding style:

```
pip install -e .[pre-commit]
pre-commit install
```

After this, the [black](https://black.readthedocs.io) formatter,
the [pylint](https://www.pylint.org/) linter
and the [pylint](https://www.pylint.org/) code analyzer will
run at every commit.

If you ever need to skip these pre-commit hooks, just use:

```
git commit -n
```

You should also keep the pre-commit hooks up to date periodically, with:

```
pre-commit autoupdate
```

Or consider using [pre-commit.ci](https://pre-commit.ci/).

## Continuous integration

`aiida-atoms` comes with a `.github` folder that contains continuous integration tests on every commit using [GitHub Actions](https://github.com/features/actions). It will:

1. run all tests
2. build the documentation
3. check coding style and version number (not required to pass by default)

## Building the documentation

> 1. Install the `docs` extra:
>
>    ```
>    pip install -e .[docs]
>    ```
>
> 2. Edit the individual documentation pages:
>
>    ```
>    docs/source/index.rst
>    docs/source/developer_guide/index.rst
>    docs/source/user_guide/index.rst
>    docs/source/user_guide/get_started.rst
>    docs/source/user_guide/tutorial.rst
>    ```
>
> 3. Use [Sphinx] to generate the html documentation:
>
>    ```
>    cd docs
>    make
>    ```

Check the result by opening `build/html/index.html` in your browser.

## Publishing the documentation

Once you're happy with your documentation, it's easy to host it online on [ReadTheDocs]:

> 1. Create an account on [ReadTheDocs]
> 2. Import your `aiida-atoms` repository (preferably using `aiida-atoms` as the project name)

The documentation is now available at [aiida-atoms.readthedocs.io](http://aiida-atoms.readthedocs.io/).

## PyPI release

Your plugin is ready to be uploaded to the [Python Package Index](https://pypi.org/).
Just register for an account and use [flit](https://flit.readthedocs.io/en/latest/upload.html):

```
pip install flit
flit publish
```

After this, you (and everyone else) should be able to:

```
pip install aiida-atoms
```

You can also enable *automatic* deployment of git tags to the python package index:
simply generate a [PyPI API token](https://pypi.org/help/#apitoken) for your PyPI account and add it as a secret to your GitHub repository under the name `pypi_token` (Go to Settings -> Secrets).

[readthedocs]: https://readthedocs.org/
[sphinx]: https://www.sphinx-doc.org/en/master/

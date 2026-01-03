# GSaPDef: Generic Sample and Profile Definitions

`GSaPDef` is a simple and flexible framework for defining and working with generic sample/profile models in a scientific context in Python.

## Features

Currently the package provides various datatypes including:

- a customizable material
- multiple types of layers such as:
  - a substrate layer
  - a (vertically) expanded layer
  - an abstract layer stack (e.g. for repeated multilayers)
- a container profile to hold the layers

Additionally, the package provides functionality to:

- Validate the defined models and their parameters
- Planned: Serialize and de-serialize models to/from common formats (e.g., txt, JSON)

## Dependencies

- `returns[mypy-compatible]`

## Installation

The package is setup in a standard Python project structure.
As such the package can be installed by either building it from source, installing a pre-build binary or (Planned) via PyPI.

### Build from source

By cloning the repository and building it locally (requires the package `build`).

```bash
git clone <repository_url> GSaPDef
cd GSaPDef
python -m build
```

Using the generated distribution files in the `dist/` folder, you can install the package via pip:

```bash
pip install dist/gsapdef-<version>-py3-none-any.whl
```

Or directly install it to the currently active environment using:

```bash
pip install .
```

while inside the cloned repository directory.

### Install from a pre-build binary

Download the latest pre-build binary from the `releases` section of the repository and install it via pip:

```bash
pip install gsapdef-<version>-py3-none-any.whl
```

## Documentation

The documentation of this package is available via the markdown files in the `docs/` folder or by starting a local MkDocs server (requires `mkdocs`):

```bash
python -m mkdocs serve
```

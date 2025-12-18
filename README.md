# GenSamplDef : Generic Sample Definitions

`GenSamplDef` is a simple and flexible framework for defining and working with generic sample/profile models in a scientific context in Python. 
It allows users to define models using a straightforward syntax to represent real world experimental setups for simulations and data analysis.

## Features

Currently the package supports various datatypes including:
- a customizable material
- multiple types of layers such as:
  - a substrate layer 
  - a (vertically) expanded layer
  - an abstract layer stack (e.g. for repeated multilayers)
- a container profile to hold the layers

Additionally, the package provides functionality to:
- Validate the defined models and their parameters
- WIP: Serialize and deserialize models to/from common formats (e.g., txt, JSON)

## Installation

The package is setup in a standard Python project structure. 
You can either:

## Build from source
By cloning the repository and building it locally (requires the package `build`).
```bash
git clone <repository_url>
cd GenSamplDef
python -m build
```
Using the generated distribution files in the `dist/` folder, you can install the package via pip:
```bash
pip install dist/gensampldef-<version>-py3-none-any.whl
```

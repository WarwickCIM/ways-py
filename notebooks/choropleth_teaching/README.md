Installation and usage notes

1. `OSError: Could not find lib c or load any of its variants` may require `pip install --upgrade --force-reinstall shapely`
2. `UserWarning: Unable to determine GEOS version` or `Proj 8.0.0 must be installed` on the Mac may require `brew install geos` and/or `brew install proj`
3. Launch the notebook using `poetry run jupyter notebook`. [Note: this should start Jupyter in a venv containing the project dependencies, but that doesn't seem to work.]

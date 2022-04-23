jupyter:
    poetry build
    pip install ./dist/notia-0.1.0-py3-none-any.whl --force-reinstall --no-deps 
    poetry run jupyter notebook

cov:
    poetry run pytest -s --cov=notia tests/ 

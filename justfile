jupyter:
    poetry build
    pip install ./dist/notia-0.3.0-py3-none-any.whl --force-reinstall --no-deps 
    poetry run jupyter notebook

cov:
    poetry run pytest -s --cov=notia tests/ 

release version:
    @echo 'Releasing {{version}}…'
    git commit --allow-empty -m "Release {{version}}"
    git tag -a {{version}} -m "Version {{version}}"
    git push -u --tags

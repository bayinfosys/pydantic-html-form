build:
	python -m build --wheel

clean:
	rm -drf dist build pydform.egg-info
	find . -type d -name __pycache__ -exec rm -r {} \+

serve:
	uvicorn --log-level=debug pydform.examples.dict-field.main:app --reload

test:
	pytest -vv .

live-test:
	watchfiles 'pytest .'

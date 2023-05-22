.PHONY: clean_coverage test_coverage distclean distcheck dist

clean_coverage:
	rm -f .coverage

test_coverage: clean_coverage
	PYTHONPATH=. pytest --cov-report=xml --cov-append --cov-branch --cov pandas_appender -v -v test/

check_action:
	python -c 'import yaml, sys; print(yaml.safe_load(sys.stdin))' < .github/workflows/test-all.yml > /dev/null

check_azure:
	python -c 'import yaml, sys; print(yaml.safe_load(sys.stdin))' < ./azure-pipelines.yml > /dev/null

distclean:
	rm -rf dist/

distcheck: distclean
	python ./setup.py sdist
	twine check dist/*

dist: distclean
	echo "reminder, you must have tagged this commit or you'll end up failing"
	echo "  git push"
	echo "  git tag v0.x.x"
	echo "  git push --tags"
	python ./setup.py sdist
	twine check dist/*
	twine upload dist/* -r pypi

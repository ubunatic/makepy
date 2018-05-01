.PHONY: publish test-publish sign

sign:
	# sign the dist with your gpg key
	gpg --detach-sign -a dist/*.whl

test-publish:
	# upload to testpypi (needs valid ~/.pypirc)
	twine upload --repository testpypi dist/*

PY2_WHEEL = $(shell find dist -name '$(PKG)*py2-none-any*.whl')
PY3_WHEEL = $(shell find dist -name '$(PKG)*py3-none-any*.whl')
publish: clean dists sign
	# upload to pypi (requires pypi account)
	twine upload --repository pypi $(PY3_WHEEL)
	twine upload --repository pypi $(PY2_WHEEL)


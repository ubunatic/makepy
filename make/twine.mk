.PHONY: publish test-publish sign

sign:
	# sign the dist with your gpg key
	gpg --detach-sign -a dist/*.whl

test-publish:
	# upload to testpypi (needs valid ~/.pypirc)
	twine upload --repository testpypi dist/*

PY2_WHEEL = $(shell find dist -name '$(PKG)*py2-none-any*.whl')
PY3_WHEEL = $(shell find dist -name '$(PKG)*py3-none-any*.whl')
publish: bumpversion clean dists sign
	# upload to pypi (requires pypi account)
	# p3-wheel: $(PY3_WHEEL)
	# p2-wheel: $(PY2_WHEEL)
	@read -p "start upload (y/N)? " key && test "$$key" = "y"
	twine upload --repository pypi $(PY3_WHEEL) $(PY2_WHEEL)


.PHONY: publish test-publish sign

sign: dist
	# sign the dist with your gpg key
	gpg --detach-sign -a dist/*.whl

test-publish: dist
	# upload to testpypi (needs valid ~/.pypirc)
	twine upload --repository testpypi dist/*

publish: dist sign
	# upload to pypi (requires pypi account)
	twine upload --repository pypi dist/*


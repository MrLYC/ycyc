ROOTPATH := .
DEVPATH = $(ROOTPATH)/.dev
DEVMKFILE := $(DEVPATH)/makefile
SRCPATH := $(ROOTPATH)/ycyc

# ENV VARS
PYENV := env PYTHONPATH=$(ROOTPATH)
PYTHON := $(PYENV) python
PEP8 := $(PYENV) pep8 --repeat --ignore=E202,E501
PYLINT := $(PYENV) pylint --disable=I0011 --msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}"
PYTEST := $(PYENV) py.test -v
PIPINSTALL := $(PYENV) pip install -i http://pypi.douban.com/simple/

-include $(DEVMKFILE)

.PHONY: dev-mk
dev-mk:
	@echo "\033[33mmake from $(DEVMKFILE)\033[0m"

.PHONY: clean
clean:
	@find . -name "__pycache__" -type d -exec rm -rf {} \; >/dev/null 2>&1 || true
	@find . -name "*.pyc" -type f -exec rm -rf {} \; >/dev/null 2>&1 || true
	@echo "\033[33mclean $(SRCPATH)\033[0m"

.PHONY: full-clean
full-clean: clean
	@git clean -f

.PHONY: pylint
pylint:
	$(PEP8) $(SRCPATH)
	$(PYLINT) -E $(SRCPATH)

.PHONY: pylint-full
pylint-full:
	$(PYLINT) $(SRCPATH)

.PHONY: test
test: pylint
	$(PYTEST) $(SRCPATH)/tests/

.PHONY: requires
requires: $(ROOTPATH)/requirements.txt
	$(PIPINSTALL) -r $(ROOTPATH)/requirements.txt

.PHONY: ipy
ipy:
	$(PYENV) ipython

.PHONY: author-config
author-config:
	git config user.email imyikong@gmail.com --local
	git config user.name MrLYC --local

.PHONY: publish
publish:
	git pull --rebase origin master --tags
	$(PYTHON) $(ROOTPATH)/setup.py clean bdist_egg sdist upload
	git tag `$(PYTHON) $(ROOTPATH)/setup.py --version`
	git push origin master:master --tags

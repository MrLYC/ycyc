DEVPATH ?= $(PWD)
VIRTUALENV ?= $(DEVPATH)/ycyc-venv
VENVPATH := $(VIRTUALENV)/bin

# virtual env
ifeq ($(VIRTUAL_ENV),)
PYTHON := $(PYENV) $(VENVPATH)/python
PEP8 := $(PYENV) $(VENVPATH)/pep8 --repeat --ignore=E202,E501
PYLINT := $(PYENV) $(VENVPATH)/pylint --disable=I0011 --msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}"
PYTEST := $(PYENV) $(VENVPATH)/py.test -v -x
PIPINSTALL := $(PYENV) $(VENVPATH)/pip install -i http://pypi.douban.com/simple/
VIRTUAL_ENV := $(VIRTUALENV)
endif

.PHONY: dev-mk dev-path dev-venv-path dev-venv dev-venv-relocate dev-requires dev-requires dev-init

dev-path:
	@echo "$(DEVPATH)"

dev-venv-path: $(VIRTUAL_ENV)
	@echo "$(VIRTUAL_ENV)"

dev-venv: dev-mk
	[ -e "$(VIRTUAL_ENV)" ] || \
	virtualenv "$(VIRTUALENV)" && \
	cp $(VENVPATH)/activate $(DEVPATH)/activate && \
	chmod 777 $(DEVPATH)/activate

dev-requires: dev-mk dev-venv requires $(DEVPATH)/requirements.txt
	$(PIPINSTALL) -r "$(DEVPATH)/requirements.txt"

dev-clean: dev-mk clean
	rm -rf $(VIRTUALENV)\; || true

dev-init: dev-mk $(ROOTPATH)/.git dev-requires
	cp $(DEVPATH)/git-hooks/* $(ROOTPATH)/.git/hooks
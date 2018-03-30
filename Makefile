PROJECT := imapfw
PACKAGE := imapfw
REPOSITORY := OfflineIMAP/imapfw


VERSION=$(shell ./imapfw.py --version)
ABBREV=$(shell git log --format='%h' HEAD~1..)
SHELL=/bin/bash
RST2HTML=`type rst2html >/dev/null 2>&1 && echo rst2html || echo rst2html.py`
DIST_FILES := dist/*.tar.gz dist/*.whl
WHEEL_FILE := dist/*.whl
EXE_FILES := dist/$(PROJECT).*
RUN=pipenv run
PYTHON=$(RUN) python

.PHONY: venv
venv:
	pipenv --venv || pipenv install --dev

all: dist

METADATA := *.egg-info

.PHONY: install
install: dist
	$(RUN) pip install $(WHEEL_FILE)


.PHONY: install_deps
install_deps: pipfile $(METADATA)

pipfile: venv Pipfile*
	pipenv install --dev
	@ touch $@

$(METADATA): setup.py
	$(PYTHON) setup.py develop
	@ touch $@

.PHONY: dist
dist: install_deps $(DIST_FILES)
$(DIST_FILES): $(MODULES) README.rst CHANGELOG.rst
	rm -f $(DIST_FILES)
	#  FIXME: --restructuredtext fails
	$(PYTHON) setup.py check --strict --metadata
	$(PYTHON) setup.py sdist
	$(PYTHON) setup.py bdist_wheel

.PHONY: test
test: install_deps $(DIST_FILES)
	$(RUN) coverage run --source=imapfw,imapfw.py -p -m imapfw.edmp
	$(RUN) coverage run --source=imapfw,imapfw.py -p -m imapfw.mmp.manager
	$(RUN) coverage run --source=imapfw,imapfw.py -p ./imapfw.py -h
	$(RUN) coverage run --source=imapfw,imapfw.py -p ./imapfw.py noop
	$(RUN) coverage run --source=imapfw,imapfw.py -p ./imapfw.py -c multiprocessing unitTests
	$(RUN) coverage run --source=imapfw,imapfw.py -p ./imapfw.py -c threading unitTests
	$(RUN) coverage run --source=imapfw,imapfw.py -p ./imapfw.py -r ./tests/syncaccounts.1.rascal -d all noop
	$(RUN) coverage run --source=imapfw,imapfw.py -p ./imapfw.py -r ./tests/syncaccounts.1.rascal -d all testRascal
	$(RUN) coverage run --source=imapfw,imapfw.py -p ./imapfw.py -r ./tests/syncaccounts.1.rascal -d all examine
	$(RUN) coverage run --source=imapfw,imapfw.py -p ./imapfw.py -r ./tests/syncaccounts.1.rascal -d all -c multiprocessing syncAccounts -a AccountA
	$(RUN) coverage run --source=imapfw,imapfw.py -p ./imapfw.py -r ./tests/syncaccounts.1.rascal -d all -c threading syncAccounts -a AccountA
	$(RUN) coverage run --source=imapfw,imapfw.py -p ./imapfw.py -r ./tests/syncaccounts.1.rascal -d all -c threading syncAccounts -a AccountA -a AccountA -a AccountA
	$(RUN) coverage combine .coverage*

clean:
	-$(PYTHON) setup.py clean --all
	-rm -f bin/offlineimapc 2>/dev/null
	-rm -rf build/
	-find . -name '*.pyc' -exec rm -f {} \;
	-find . -name '*.pygc' -exec rm -f {} \;
	-find . -name '*.whl' -exec rm -f {} \;
	-find . -name '*.class' -exec rm -f {} \;
	-find . -name '.cache*' -exec rm -f {} \;
	-rm -f manpage.links manpage.refs 2>/dev/null
	-find . -name auth -exec rm -vf {}/password {}/username \;

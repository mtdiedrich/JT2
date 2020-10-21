ACTIVATE:=venv/bin/activate
VIRTUALENV_DIR:=venv/
PIP:=venv/bin/pip

reset: clean
	pipreqs --force
	${ACTIVATE}

run:
	. ${ACTIVATE}; python jtrain/run.py $(argument)

clean:
	find . -name "*.py[co]" -delete
	rm -r venv

lint:
	. ${ACTIVATE}; flake8 ./src
	. ${ACTIVATE}; flake8 ./tests

test: ${ACTIVATE}
	${VIRTUALENV_DIR}/bin/py.test -rw tests/

${ACTIVATE}: requirements.txt
	test -d ${VIRTUALENV_DIR}/bin || virtualenv --python=python3 ${VIRTUALENV_DIR}
	${PIP} install --upgrade pip
	${PIP} install -Ur requirements.txt
	touch $@

GHC = ghc

SRCDIR := src/rottnest/rz_decomposer

SRCFILES := $(wildcard ${SRCDIR}/*.hs)
OBJFILES := $(patsubst ${SRCDIR}/%.hs, ${SRCDIR}/%, ${SRCFILES})
HIFILES := $(patsubst ${SRCDIR}/%.hs, ${SRCDIR}/%.hi, ${SRCFILES})
EXES := $(patsubst ${SRCDIR}/%.hs, ${SRCDIR}/%, ${SRCFILES})


.PHONY: all package test clean gridsynth build

all: build

build: package

package: gridsynth
	pip install -r requirements.txt
	pip install -e .

gridsynth: ${OBJFILES}

${SRCDIR}/% : ${SRCDIR}/%.hs
	$(GHC) $^

test:
	pytest --forked
	# We have to run this one separately, since importing breaks inside test systems
	python test/unit/test_plugins.py


clean :
	rm $(OBJFILES)
	rm $(EXES)
	rm $(HIFILES)
	pip uninstall rottnest

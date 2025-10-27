GHC = ghc

SRCDIR := src/rottnest/gridsynth

SRCFILES := $(wildcard ${SRCDIR}/*.hs)
OBJFILES := $(patsubst ${SRCDIR}/%.hs, ${SRCDIR}/%, ${SRCFILES})
HIFILES := $(patsubst ${SRCDIR}/%.hs, ${SRCDIR}/%.hi, ${SRCFILES})
EXES := $(patsubst ${SRCDIR}/%.hs, ${SRCDIR}/%, ${SRCFILES})


.PHONY: all package test clean gridsynth build

all: package 

package: gridsynth
	pip install -r requirements.txt
	pip install -e .

gridsynth:  ${OBJFILES}

build: package

${SRCDIR}/% : ${SRCDIR}/%.hs
	$(GHC) -package random -package newsynth $^

test:
	pytest

clean: 
	rm $(OBJFILES) || true
	rm $(EXES) || true
	rm $(HIFILES) || true
	pip uninstall rottnest

update: 
	git pull
	${MAKE} build

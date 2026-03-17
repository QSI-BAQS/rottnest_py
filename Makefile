GHC = ghc

SRCDIR := src/rottnest/gridsynth

SRCFILES := $(wildcard ${SRCDIR}/*.hs)
OBJFILES := $(patsubst ${SRCDIR}/%.hs, ${SRCDIR}/%, ${SRCFILES})
HIFILES := $(patsubst ${SRCDIR}/%.hs, ${SRCDIR}/%.hi, ${SRCFILES})
EXES := $(patsubst ${SRCDIR}/%.hs, ${SRCDIR}/%, ${SRCFILES})


.PHONY: all package test clean gridsynth build

all: package

package: gridsynth
	pip install -e .

gridsynth : ${OBJFILES}

build: gridsynth package

${SRCDIR}/% : ${SRCDIR}/%.hs
	$(GHC) $^

test:
	pytest

clean :
	rm $(OBJFILES)
	rm $(EXES)
	rm $(HIFILES)
	pip uninstall rottnest


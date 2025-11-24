GHC = ghc

SRCDIR := src/rottnest/rz_decomposer

SRCFILES := $(wildcard ${SRCDIR}/*.hs)
OBJFILES := $(patsubst ${SRCDIR}/%.hs, ${SRCDIR}/%, ${SRCFILES})
HIFILES := $(patsubst ${SRCDIR}/%.hs, ${SRCDIR}/%.hi, ${SRCFILES})
EXES := $(patsubst ${SRCDIR}/%.hs, ${SRCDIR}/%, ${SRCFILES})


.PHONY: all package test clean gridsynth build

all: package 

package: gridsynth
	pip install -e .

gridsynth : ${OBJFILES}

build : ${OBJFILES}

${SRCDIR}/% : ${SRCDIR}/%.hs
	$(GHC) -package random -package newsynth $^

test:
	pytest

clean : 
	rm $(OBJFILES)
	rm $(EXES)
	rm $(HIFILES)
	pip uninstall rottnest

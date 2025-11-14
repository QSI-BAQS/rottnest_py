GHC = ghc

SRCDIR := src/rottnest/gridsynth
SRCDIRb := src/rottnest/rz_decomposer


SRCFILES := $(wildcard ${SRCDIR}/*.hs)

OBJFILES := $(patsubst ${SRCDIR}/%.hs, ${SRCDIR}/%, ${SRCFILES})
OBJFILESb := $(patsubst ${SRCDIR}/%.hs, ${SRCDIRb}/%, ${SRCFILES})

HIFILES := $(patsubst ${SRCDIR}/%.hs, ${SRCDIR}/%.hi, ${SRCFILES})

EXES := $(patsubst ${SRCDIR}/%.hs, ${SRCDIR}/%, ${SRCFILES})


.PHONY: all package test clean gridsynth build

all: package 

package: gridsynth
	pip install -r requirements.txt
	pip install -e .

gridsynth:  ${OBJFILES} ${OBJFILESb}

build: package

${SRCDIR}/% : ${SRCDIR}/%.hs
	$(GHC) -package random -package newsynth $^

${SRCDIRb}/% : ${SRCDIRb}/%.hs
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

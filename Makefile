CC = ghc

SRCDIR := src/rottnest/rz_decomposers

SRCFILES := $(wildcard ${SRCDIR}/*.hs)
OBJFILES := $(patsubst ${SRCDIR}/%.hs, ${SRCDIR}/%.o, ${SRCFILES})
HIFILES := $(patsubst ${SRCDIR}/%.hs, ${SRCDIR}/%.hi, ${SRCFILES})
EXES := $(patsubst ${SRCDIR}/%.hs, ${SRCDIR}/%, ${SRCFILES})


.PHONY: package

all: package 


package: gridsynth
	pip install -e .


gridsynth : ${OBJFILES}

build : ${OBJFILES}

${SRCDIR}/%.o : ${SRCDIR}/%.hs
	$(CC) $^

clean : 
	rm $(OBJFILES)
	rm $(EXES)
	rm $(HIFILES)

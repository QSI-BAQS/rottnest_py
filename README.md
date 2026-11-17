## Rottnest 

Python backend for Rottnest - a utility scale fault-tolerant quantum compiler.
This handles the server backend and is the main logic between different modules. 


This repository handles the plugin interface for `executables`, `architectures`, `rz_decomposers` and `error_budgets`.
Additionally it performs parsing and chunking of utility scale quantum algorithms that match the interface specification. 

Currently supported languages:
- Cirq
- Qualtran
- pyLIQTR 
- QASM 2.0/3.0 (Cirq parsing subset)


# Installation

For pyLIQTR compatibility `rottnest` currently depends on Python 3.11. 
It is suggested to set it up in a clean python environment (conda or venv) with the correct version. 
For automatic plugin installation see the main rottnest repository which will also manage the installation of this repository. 


## Dependencies:

Depends on:
- Rottnest Nodejs for frontend 
- Cabaliser for graph state compilation
  - Requires Pauli Tracker for tracking and scheduling
  - Requires Pandora for pandora integration
- t_scheduler for Simulation  
- Gridsynth for Rz Decomposition 

Gridsynth is run as a subprocess to ensure license separation.
There are hooks set up to swap it for other Rz decomposers.

## Installation 

Gridsynth requires quipper. See instructions below to install Quipper 

Next we can install
- pip install -e . 

## Gridsynth Installation ##

Currently GridSynth is partially merged into Quipper, so it follows that if we can install quipper then GridSynth should work.

Quipper is currently in a Haskell dependency hell, newer versions of ghc will not compile it, and newer versions of Cabal are incompatible with various dependencies of Quipper (newer versions of the dependencies are in turn incompatible with versions of ghc that are compatible with Quipper). As a result ghc 8.6.5 is stable, though 8.8.4 may or may not also work.

We'll version quipper using ghcup, you may look into your own nix, cabal or stack based solutions to this problem. This currently works as Cabal will invoke the legacy v1 installation methods, this may be unstable in the future.

```
    curl https://gitlab.haskell.org/haskell/ghcup/raw/master/ghcup > /tmp/ghcup
    chmod +x /tmp/ghcup
    /tmp/ghcup install 8.6.5
    /tmp/ghcup set 8.6.5
    /tmp/ghcup install-cabal 2.4.1.0

    # Update path
    PATH="$HOME/.cabal/bin:$HOME/.ghcup/bin:$PATH"

    # Install Quipper
    cabal update
    cabal install quipper-all
```
You may wish to add the path command to your terminal's appropriate rc file. Rather than installing quipper you may also install newsynth independently.

For more details see the quipper docs: (https://www.mathstat.dal.ca/~selinger/quipper/README)[https://www.mathstat.dal.ca/~selinger/quipper/README]

Once that's installed we can compile the relevant Haskell files 
```
make gridsynth 
```

Once this is done now we can install the package
```
python setup.py install
```

# Execution

The server entrypoint is `python src/rottnest/server/server.py`
Additionally with the inclusion of the appropriate architecture plugin modules, `rottnest` may be used as a library.  
See the `rottnest_example_executables` repository for some sample executable modules, along with `t_scheduler` or one of the other architecture modules to set up a simple build environment. 



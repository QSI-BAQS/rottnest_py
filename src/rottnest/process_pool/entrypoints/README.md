# Entrypoints

The purposes of these functions is to control the spawning of processes

This class provides a relative context for what the entrypoint is spawning in, and by extension allows or disallows the spawning of subprocesses in the wrong contexts.

## entrypoint.py
Base entrypoint class

- `ProcessEntrypoint()`
  - Base class for single instantiation of entrypoints 
  - `entrypoint`
    - Class method to trigger the runner of the process, this runs on the spawned process
  - `get_entrypoint`
    - Wraps valiation and returns the entrypoint function
    - This resolves on the spawning process, before passing the entrypoint function 
  - `run`
    - Runner for the process, invoked by entrypoint
  - `__call__`
    - Operator overload to `run` 
  - `blockers`
    - Setup of blocking types on other process types
  - `setup`
    - Environment setup handler
  - `main`
    - Main caller
  - `finalise`
    - Finalisation methods on the process
  - `join`
    - Operations to kill the process

- `get_current_process_handler()`
Getter for handler of the process entrypoint
  
## process_type.py
Types and typing rules for proceses.
This file also includes the spawning rules for processes.
Process spawning requires a matching of the SPAWN rules

- `ProcessType`
  - Process type singleton, contains spawn rules
  - Constrained to a single instantiation per process
- `get_type()`
  - Gets the current process type
- `set_type(process_type: str)`
  - Sets the current process type
- `validate(spawn_type: str)` 
  - Validates that the current process can spawn a subprocess or type

## pool_api.py
Process pool spawn context using `process_type.SERVER`
- `PoolAPIHandler`
  - Class for the process pool api holding process 
- `entrypoint()`
  - Dispatch method entrypoint 


## pool_manager.py
Process pool spawn context using `process_type.POOL_MANAGER`
- `PoolManagerProcessHandler`
  - Class for the process pool subprocess 
- `get_entrypoint()`
  - Dispatch method entrypoint 

## pool_worker.py
Process pool worker spawn context using `process_type.POOL_WORKER`
- PoolWorkerProcessHandler
  - Class for worker subprocesses 

## priority_worker.py
Priority worker spawn context. Currently defaults to worker spawn context.


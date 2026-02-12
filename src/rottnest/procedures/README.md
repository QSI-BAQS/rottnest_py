# Rottnest Compilation Pass Management

The files here handle Rottnest compilation passes.
A pass is termed a `procudure` due to keywords in Python.

- Each procedure manages a set of stages, and acts as a compilation environment.
- Stages are uniquely identified via an overloadable tag field.
- Stages list other tags as dependencies.

- When executed, a procedure will look for a stage where all dependencies are resolved and execute it 
  - If the stage executes correctly, then that tag is bound to the namespace of the procedure object 
    - This implies that any tag which a stage depends on is also an element of the procedure/environment
  - If no such stage exists, and there are still unresolved stages an exception is thrown
  
Procedures inherit from the Stage class, and hence a procedure may also be a stage in a larger procedure.


# TODO
- Expose procedures to the plugin manager

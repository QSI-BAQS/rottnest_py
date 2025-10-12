# Rottnest-Py Unit Testing

Note: Pandora does not have to be running, although the tests will attempt to connect to it.

Tests can be run with `python -m unittest <test_name>`. Directly running a test (ie. `python <test_name>.py`) does not appear to currently work (possibly due to Pandora?).

## `dummy_arch`

`dummy_arch` provides a non-functional architecture module, to be used when testing Plugin loading. It DOES NOT FUNCTION as an architecture.

## `utils`

### `arch_factory`

`arch_factory` provides a way to dynamically create arbitrary architectures and their consituent components (Designer, Composer, Worker).

`build_arch(arch_name: str, designer, composer, worker) -> Type<RottnestArchitecture>` will create an architecture with the given components. Any un-needed components can be omitted and will be `None`.

`build_worker`, `build_designer`, `build_composer` all operate as `(component_name, **attrs) -> Type<*>`, allowing arbitrary components to be built with any required attributes.


### `declarative_qualtran`

`declartive_qualtran` provides a way to build Qualtran `Bloq`s in a declarative manner (similar to Cirq).

It provides a single function, `build_bloq(registers, *gates) -> Bloq`, where `registers` is a collection of named (as strings) registers, and `gates` is a collection of tuples of the form `(gate, registers: Dict<str, str>)`.

eg.
```
bloq = BloqBuilder()
x = bloq.add_register('x', 1)
y = bloq.add_register('y', 1)
x, y = bloq.add(CNOT(), ctrl=x, target=y)
res = bloq.finalize(x=x, y=y)
```

is mostly equivalent to

```
res = build_bloq(
  registers = ('x', 'y'),
  gates = [
    (CNOT(), {'ctrl': 'x', 'target': 'y'})
  ]
)
```

with the caveat that `build_bloq` results in a regular `Bloq` (specifically, a `CustomBloq`, a subclass of `Bloq`) rather than a `CompositeBloq`.

from typing import Type

from rottnest.architecture_interface import rottnest_architecture, rottnest_designer, rottnest_composer, rottnest_worker

def build_arch(arch_name,
               designer: Type['RottnestDesigner'] | None = None,
               composer: Type['RottnestComposer'] | None = None,
               worker: Type['RottnestWorker'] | None = None):
    def get_name() -> str:
        return arch_name

    return type(arch_name, (rottnest_architecture.RottnestArchitecture,),
                dict(
                     get_name=staticmethod(get_name),
                     designer=designer,
                     composer=composer,
                     worker=worker
                )
    )

def build_worker(worker_name, **attrs):
    return type(worker_name, (rottnest_worker.RottnestWorker,), attrs)

def build_designer(designer_name, **attrs):
    return type(designer_name, (rottnest_designer.RottnestDesigner,), attrs)

def build_composer(composer_name, **attrs):
    return type(composer_name, (rottnest_composer.RottnestComposer,), attrs)

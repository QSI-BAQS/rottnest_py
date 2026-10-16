from rottnest.plugins import plugin_managers

from . import factory

for manager in plugin_managers:
    cls_name = manager.__class__.__name__.split('Plugin')[0]
    stages = factory.option_stages_factory(cls_name, manager)

    for name, stage in stages.items():
        locals()[name] = stage

    # TODO: Procedure factory

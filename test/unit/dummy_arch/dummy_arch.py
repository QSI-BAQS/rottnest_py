from rottnest.architecture_interface import rottnest_architecture, rottnest_designer, rottnest_composer, rottnest_worker


class DummyDesigner(rottnest_designer.RottnestDesigner):
    @staticmethod
    def get_mem_bound(layout):
        return None



class DummyComposer(rottnest_composer.RottnestComposer):
    @staticmethod
    def results_composer_constructor():
        return DummyResComposer


class DummyResComposer(rottnest_composer.ResultsComposer):
    pass


class DummyWorker(rottnest_worker.RottnestWorker):
    pass




class DummyArchitecture(rottnest_architecture.RottnestArchitecture):
    designer = DummyDesigner

    composer = DummyComposer

    worker = DummyWorker

    @staticmethod
    def get_name() -> str:
        return "Dummy"

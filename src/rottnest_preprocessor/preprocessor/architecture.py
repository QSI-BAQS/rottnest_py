'''
    Preprocessor architecture object
'''
from rottnest.architecture_interface import rottnest_architecture

from .rz_collection_worker import RzCollectionWorker
from .rz_collection_composer import RzCollectionComposer
from .designer import PreprocessDesigner


class PreprocessorArchitecture(rottnest_architecture.RottnestArchitecture):
    '''
        Preprocessor architecture object
        Wraps parsing Rz and T counting using the same
         execution paths and pool logic as the main
         compilation
    '''

    worker = RzCollectionWorker
    composer = RzCollectionComposer
    designer = PreprocessDesigner

    @staticmethod
    def get_name() -> str:
        return "Rz Counter"

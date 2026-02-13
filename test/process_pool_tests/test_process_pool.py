'''
    Tests process pool execution
'''
import time

import unittest
import math

import cirq

# These workers have been tested without the pool elsewhere
from rottnest.compute_units.layout_proxy import LayoutProxy

from rottnest.preprocessor.architecture import PreprocessorArchitecture

from rottnest.process_pool.process_pool import ComputeUnitExecutorPool
from rottnest.process_pool.singleton import get_pool
from rottnest.process_pool.pool_status import PoolStatus

from rottnest.plugins import architectures, executables

from rottnest import test_utils
from rottnest.test_utils.executable import SampleExecutable 
from rottnest.test_utils.plugin_support import add_executable, add_architecture


layout_id = 0
memory_bound = 1000
layout = {'mem_bound': memory_bound}
LayoutProxy.add_layout_with_id(layout_id, layout)

class ProcessPoolTests(unittest.TestCase):

    def test_ping(self):
        '''
            Tests ping through ipc
        '''

        executables.load_modules_from_strings(test_utils.__file__)
        executables.set_current_executable(SampleExecutable.get_name())
        architectures.set_current_architecture(
            'Rz Counter' 
        )


        pool = ComputeUnitExecutorPool() 
        pool.start()

        # Asserts correctness in here
        pool.ping_manager()
        pool.shutdown()
       
    def test_ping_workers(self):
        '''
            Tests ping through ipc
        '''

        executables.load_modules_from_strings(test_utils.__file__)
        executables.set_current_executable(SampleExecutable.get_name())
        architectures.set_current_architecture(
            'Rz Counter' 
        )

        pool = ComputeUnitExecutorPool() 
        pool.start()

        # Asserts correctness in here
        pool.ping_manager()
       
        # Synch pool state 
        pool.synchronise()

        # Setup the pool
        pool.set_architecture_module(
            'Rz Counter' 
        )
        pool.set_executable(
            'Sample Executable'
        )
        pool.set_executable_params({})

        # Start workers
        pool.start_workers()

        # Asserts correctness in here
        pool.ping()
        pool.shutdown()


    def test_pool_status(self):
        '''
            Test setting and getting executables and architectures
        '''

        rz_counter = 'Rz Counter'
        sample = 'Sample Executable'

        executables.load_modules_from_strings(test_utils.__file__)
        executables.set_current_executable(SampleExecutable.get_name())


        pool = get_pool() 
        pool.start()

        status = pool.get_synchronisation_status()
        assert status[:2] == [None, None]

        architectures.set_current_architecture(
            rz_counter 
        )
        executables.set_current_executable(
            sample 
        )

        pool.synchronise()

        status = pool.get_synchronisation_status()
        assert status[:2] == [rz_counter, sample]

        pool.shutdown()

    def test_process_pool(self):
        '''
            Tests executing the process pool with an Rz counter architecture 
        '''

        executables.load_modules_from_strings(test_utils.__file__)
        executables.set_current_executable(SampleExecutable.get_name())
        architectures.set_current_architecture(
            'Rz Counter' 
        )


        pool = ComputeUnitExecutorPool() 
        pool.start()

        # Asserts correctness in here
        pool.ping_manager()
       
        # Synch pool state 
        pool.synchronise()

        # Setup the pool
        pool.set_architecture_module(
            'Rz Counter' 
        )
        pool.set_executable(
            'Sample Executable'
        )
        pool.set_executable_params({})

        # Start workers
        pool.start_workers()
         
        # Run the sequence
        pool.run_sequence([layout_id])
        
        while pool.poll() != PoolStatus.FINISHED:
            # Example busy wait
            print("Executing...")
            time.sleep(1)

        # Shutdown the pool
        pool.shutdown()
        print("Triggered shutdown")
        return

    def test_process_pool_from_singletons(self):
        '''
            Tests executing the process pool with an Rz counter architecture 
        '''

        executables.load_modules_from_strings(test_utils.__file__)
        executables.set_current_executable(SampleExecutable.get_name())
        architectures.set_current_architecture('Rz Counter')

        pool = get_pool() 
        pool.start()

        # Asserts correctness in here
        pool.ping_manager()
       
        # Synch pool state 
        pool.synchronise()

        # Start workers
        pool.start_workers()
         
        # Run the sequence
        pool.run_sequence([layout_id])
        
        while pool.poll() != PoolStatus.FINISHED:
            # Example busy wait
            print("Executing...")
            time.sleep(1)

        # Shutdown the pool
        pool.shutdown()
        print("Triggered shutdown")
        return


if __name__ == '__main__':
    obj = ProcessPoolTests()
    obj.test_ping()
    obj.test_ping_workers()
    obj.test_pool_status()

    #obj.test_pool_status()
    #obj.test_process_pool_from_singletons()

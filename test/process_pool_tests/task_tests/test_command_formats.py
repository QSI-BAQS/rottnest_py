import unittest
from rottnest.process_pool.tasks import get_pool_manager_tasks
from rottnest.process_pool.tasks.pool_task import PoolTask, PriorityWorkerTask


class CommandFormatTest:
    '''
        Simple check on keys
    '''

    def test_pool_tasks(self):
        '''
            Checks command formats for pool tasks
        '''
        for task_key, task in get_pool_manager_tasks().items(): 
            
            # Test priority workers elsewhere
            if isinstance(task, PriorityWorkerTask):
                continue

            assert isinstance(task_key, str)
            assert isinstance(task.get_command(), str)
            assert isinstance(task.get_poll_key(), str)
            assert isinstance(task.get_finalise_key(), str)

    def test_priority_worker_tasks(self):
        '''
            Checks command formats for pool tasks
        '''
        for task_key, task in get_pool_manager_tasks().items(): 
            
            # Test priority workers elsewhere
            if not isinstance(task, PriorityWorkerTask):
                continue

            assert isinstance(task_key, str)
            assert isinstance(task.get_command(), str)
            assert isinstance(task.get_poll_key(), str)
            assert isinstance(task.get_finalise_key(), str)
            assert isinstance(task.get_priority_worker_command(), str)

if __name__ == '__main__':
    tst = CommandFormatTest()
    tst.test_pool_tasks()
    tst.test_priority_worker_tasks()


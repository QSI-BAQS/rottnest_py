'''
    Entrypoint script for launching rottnest with MPI
'''

import sys

import json

from queue import Queue

from mpi4py import MPI

from rottnest.mpi.mpi_pool_manager import MPIPoolManager
from rottnest.mpi.mpi_queue import MPIClientQueue

from rottnest.process_pool import commands, symbols

from rottnest.plugins import architectures, executables


def root_main(comm, architecture, executable, layouts):
    '''
        Main function for the root process (manager)
    '''
    pool_task_queue = Queue()
    pool_completion_queue = Queue()
    pool_prio_task_queue = Queue()
    pool_prio_completion_queue = Queue()

    pool_manager = MPIPoolManager(
        pool_task_queue, pool_completion_queue,
        pool_prio_task_queue, pool_prio_completion_queue,
        comm
    )

    pool_manager._precision = executables.get_precision()

    '''
        This process has to play the role of a manager (since it is standalone)
        However, some manager tasks have already been complete pre-divergence:
        - Loading layouts
        - Loading architecture and executable modules
        - Setting precision

        Hence, all we need to do now is;
        - Send the RUN_SEQUENCE command to run the standalone job
        - Send STOP_WORKERS, TERMINATE to clean up
        - Read from the completion queue
    '''

    # We queue these up in advance, to be consumed below
    pool_task_queue.put(
        (
            commands.RUN_SEQUENCE,
        )
    )

    pool_task_queue.put(
        (
            commands.STOP_WORKERS,
        )
    )

    pool_task_queue.put(
        (
            commands.TERMINATE,
        )
    )

    # Run each task
    while not pool_task_queue.empty():
        pool_manager.run_task()

    # Handle all completions
    while not pool_completion_queue.empty():
        # TODO : This should handle the queued items properly
        print(pool_completion_queue.get())


def worker_main(comm, architecture, layouts):
    '''
        Main function for the worker process(es)
    '''
    worker = architecture.worker()
    queue = MPIClientQueue()

    # Queue is two way, and so is used for both tasks in and results out
    worker.main(queue, queue)


def main(architecture_name, executable_name, layouts):
    '''
        Handles common behaviour before diverging to root/worker behaviour
    '''
    comm = MPI.COMM_WORLD

    # Load arch, exe and layouts
    architectures.set_current_architecture(architecture_name)
    executables.set_current_executable(executable_name)

    architecture = architectures.get_current_architecture()
    executable = executables.get_current_executable()

    for layout_id, layout in layouts:
        # TODO : Load layouts by id into proxy

    if comm.Get_rank() == 0:
        root_main(comm, architecture, executable, layouts)
    else:
        worker_main(comm, architecture, layouts)

    print(f"MPI peer {comm.Get_rank()} completed")


def launch():
    '''
        Handles arg parsing before delegating to main
    '''
    args = sys.argv[1:]

    if len(args) != 3 or args[0] in ["help", "--help"]:
        # Ensure only one help message is printed
        if MPI.COMM_WORLD.Get_rank() == 0:
            print(
'''rottnest_mpi <architecture_name> <executable_name> <layout_file> [OPTIONS...]

USAGE:

    An MPI-backed standalone rottnest executor.
    Must be run via mpirun, and intended to be launched as part of a slurm job.

    Given n MPI peers, runs a manager and n-1 clients, with clients doing
    distributed work.

    <architecture_name>
        The name of the architecture to use.
        Tries to load the architecture as a Python module, then falls
        back to a filepath

    <executable_name>
        As above, but for an executable.

    <layout_file>
        A file to load the layout JSON(s) from.

OPTIONS:
    -a <module path>
        Provide a module to load as a source of architectures
        Should be either a Python import path, or a regular file-path to a
        Python file providing the architectures

    -e <module path>
        As above, but for executable modules

    -o <file>
        Provides a file to write the result to (as opposed to dumping it to stdout)'''
            )
        exit(0)

    # For now, panic if there is only one process
    if MPI.COMM_WORLD.Get_size() == 1:
        # TODO : Attempt local instead?
        print("rottnest_mpi requires at least two processes to function")
        exit(1)


    # TODO : Proper arg parsing (imports + output)

    arch_name = args[0]
    exe_name = args[1]
    layout_file = args[2]

    # Open layout file and load layout
    # (currently single layout only, no validation)
    layouts = None
    try:
        with open(layout_file, 'r') as lf:
            layout_data = lf.read()

            layouts = {0: json.loads(layout_data)}
    except Exception as e:
        print(f"Failed to open file '{layout_file}' : {e}")
        exit(1)

    main(arch_name, exe_name, layouts)


if __name__ == "__main__":
    launch()

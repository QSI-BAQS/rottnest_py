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


class RottnestMPIArgs():
    '''
        Argument parsing
    '''
    STATE_OPEN = object()
    STATE_LOAD_MODULE = object()
    STATE_SET_OUTPUT_FILE = object()
    STATE_CLOSED = object()


    def __init__(self):
        self.output_file = None
        self.modules_to_load = set()

        self.architecture_name = None
        self.executable_name = None
        self.layout_file = None

        self.state = RottnestMPIArgs.STATE_OPEN

        self.state_handlers = {
            RottnestMPIArgs.STATE_OPEN: self.handle_arg_state_open,
            RottnestMPIArgs.STATE_LOAD_MODULE: self.handle_arg_state_load_module,
            RottnestMPIArgs.STATE_SET_OUTPUT_FILE: self.handle_arg_state_set_output_file,
            # No-Op bound to closed state
            RottnestMPIArgs.STATE_CLOSED: lambda *a: None
        }

        self.open_flag_handlers = {
            "--help": self.help,
            "-m": lambda s: RottnestMPIArgs.STATE_LOAD_MODULE,
            "--module": lambda s: RottnestMPIArgs.STATE_LOAD_MODULE,
            "-o": lambda s: RottnestMPIArgs.STATE_SET_OUTPUT_FILE,
            "--output_file": lambda s: RottnestMPIArgs.STATE_SET_OUTPUT_FILE
        }

    def help(self):
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
    -m/--module <module path>
        Provide a module to load as a source of architectures/executables
        Should be either a Python import path, or a regular file-path to a
        Python file providing the architectures/executables
        Can be provided any number of times

    -o/--output_file <file>
        Provides a file to write the result to (as opposed to dumping it to stdout)'''
        )
        return RottnestMPIArgs.STATE_CLOSED


    def parse(self, arg):
        self.state_handlers[self.state](arg)

    def handle_arg_state_open(self, arg):
        if arg in self.open_flag_handlers.keys():
            self.state = self.open_flag_handlers[arg](self)
        elif arg[0] == "-":
            print(f"Error: unknown flag '{arg}'")
            self.state = RottnestMPIArgs.STATE_CLOSED
        else:
            if self.architecture_name is None:
                self.architecture_name = arg
            elif self.executable_name is None:
                self.executable_name = arg
            elif self.layout_file is None:
                self.layout_file = arg

    def handle_arg_state_load_module(self, arg):
        if arg[0] == "-":
            print(f"Expected module name, got flag '{arg}'")
            self.state = RottnestMPIArgs.STATE_CLOSED
        else:
            self.modules_to_load.add(arg)
            self.state = RottnestMPIArgs.STATE_OPEN

    def handle_arg_state_set_output_file(self, arg):
        if arg[0] == "-":
            print(f"Expected output file path, got flag '{arg}'")
            self.state = RottnestMPIArgs.STATE_CLOSED
        elif self.output_file is not None:
            print(f"Output file was already set to '{self.output_file}', please set exactly one output file")
            self.state = RottnestMPIArgs.STATE_CLOSED
        else:
            self.output_file = arg
            self.state = RottnestMPIArgs.STATE_OPEN

    def finalise(self) -> bool:
        if self.architecture_name is None:
            print("No architecture name was provided")
            return False
        elif self.executable_name is None:
            print("No executable name was provided")
            return False
        elif self.layout_file is None:
            print("No layout file was provided")
            return False
        # We tried to finalise while not in an open state
        elif self.state is not RottnestMPIArgs.STATE_OPEN:
            if self.state is RottnestMPIArgs.STATE_LOAD_MODULE:
                print("Arguments ended while expecting a module name")
            elif self.state is RottnestMPIArgs.STATE_SET_OUTPUT_FILE:
                print("Arguments ended while expecting an output file")
            return False

        return True


    @staticmethod
    def from_args(*args):
        res = RottnestMPIArgs()
        for arg in args:
            res.parse(arg)

        if not res.finalise():
            return None
        return res




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
        pass
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
    argv = sys.argv[1:]

    # Silence non-root processes
    if MPI.COMM_WORLD.Get_rank() != 0:
        sys.stdout = type("DummyWriter", tuple(), dict(write=lambda *a, **ka: None, flush=lambda *a, **ka: None))

    # Parse args
    args = RottnestMPIArgs.from_args(*argv)

    if args is None:
        exit(1)

    # For now, panic if there is only one process
    if MPI.COMM_WORLD.Get_size() == 1:
        # TODO : Attempt local instead?
        print("rottnest_mpi requires at least two processes to function")
        exit(1)


    # Open layout file and load layout
    # (currently single layout only, no validation)
    layouts = None
    try:
        with open(args.layout_file, 'r') as lf:
            layout_data = lf.read()

            layouts = {0: json.loads(layout_data)}
    except Exception as e:
        print(f"Failed to open file '{args.layout_file}' : {e}")
        exit(1)

    main(args.architecture_name, args.executable_name, layouts)


if __name__ == "__main__":
    launch()

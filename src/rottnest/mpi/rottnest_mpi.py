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

from rottnest.compute_units.layout_proxy import LayoutProxy

from rottnest.plugins import architectures, executables

def perror(msg, *args, **kwargs):
    print("[ ERROR ] " + msg, *args, **kwargs, file=sys.stderr)


class MPIArgState():
    '''
        A state in the arg parsing state machine

        transition_fn must return the next state
    '''
    def __init__(self, transition_fn, final=False):
        self.transition_fn = transition_fn
        self.final = final


    def __call__(self, *args, **kwargs):
        return self.transition_fn(*args, **kwargs)


class RottnestMPIArgs():
    '''
        Argument parsing
    '''
    @staticmethod
    def _handle_state_open(instance, arg, *_):
        flag_handlers = {
            "--help": RottnestMPIArgs._help,
            "-m": lambda *a: RottnestMPIArgs.STATE_LOAD_MODULE,
            "--module": lambda *a: RottnestMPIArgs.STATE_LOAD_MODULE,
            "-o": lambda *a: RottnestMPIArgs.STATE_SET_OUTPUT_FILE,
            "--output_file": lambda *a: RottnestMPIArgs.STATE_SET_OUTPUT_FILE,
            "-p": lambda *a: RottnestMPIArgs.STATE_SET_PARAM_FILE,
            "--param_file": lambda *a: RottnestMPIArgs.STATE_SET_PARAM_FILE,
        }

        instance.back_arg = arg

        if arg in flag_handlers:
            return flag_handlers[arg]()

        if arg[0] == "-":
            instance.error_msg = f"Unknown flag '{arg}'"
            return RottnestMPIArgs.STATE_CLOSED

        if instance.outstanding_attributes:
            instance.attributes[instance.outstanding_attributes.pop(0)] = arg
            return RottnestMPIArgs.STATE_OPEN

        instance.error_msg = f"Was not expecting more unbound arguments, got '{arg}'"
        return RottnestMPIArgs.STATE_CLOSED

    STATE_OPEN = MPIArgState(transition_fn=_handle_state_open, final=True)


    @staticmethod
    def _handle_load_module(instance, arg, *_):
        if arg[0] == "-":
            instance.error_msg = f"Expected module name, got flag '{arg}'"
            return RottnestMPIArgs.STATE_CLOSED
        instance.modules_to_load.add(arg)
        return RottnestMPIArgs.STATE_OPEN

    STATE_LOAD_MODULE = MPIArgState(transition_fn=_handle_load_module)


    @staticmethod
    def _handle_set_output_file(instance, arg, *_):
        if instance.output_file is not None:
            instance.error_msg = f"Output file should only be set once"
            return RottnestMPIArgs.STATE_CLOSED
        if arg[0] == "-":
            instance.error_msg = f"Expected output file, got flag '{arg}'"
            return RottnestMPIArgs.STATE_CLOSED
        instance.output_file = arg
        return RottnestMPIArgs.STATE_OPEN

    STATE_SET_OUTPUT_FILE = MPIArgState(transition_fn=_handle_set_output_file)


    @staticmethod
    def _handle_set_param_file(instance, arg, *_):
        if instance.param_file is not None:
            instance.error_msg = f"Parameter file should only be set once"
            return RottnestMPIArgs.STATE_CLOSED
        if arg[0] == "-":
            instance.error_msg = f"Expected parameter file, got flag '{arg}'"
            return RottnestMPIArgs.STATE_CLOSED
        instance.param_file = arg
        return RottnestMPIArgs.STATE_OPEN

    STATE_SET_PARAM_FILE = MPIArgState(transition_fn=_handle_set_param_file)


    STATE_CLOSED = MPIArgState(transition_fn=lambda *a, **ka: STATE_CLOSED)


    STATE_CLOSED_HELP = MPIArgState(transition_fn=lambda *a, **ka: STATE_CLOSED_HELP)


    @staticmethod
    def _help(*_):
        print(
'''rottnest_mpi <architecture_name> <executable_name> <layout_file> [OPTIONS...]

USAGE:
    An MPI-backed standalone rottnest executor.
    Must be run via mpirun, and intended to be launched as part of a slurm job.

    Given n MPI peers, runs a manager and n-1 clients, with clients doing
    distributed work.

    <architecture_name>
        The name of the architecture to use.
        Will attempt to load the architecture from any available modules, which can either
        be explicitly used (see -m) or loaded as part of your rottnest config.

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
        Provides a file to write the result to (as opposed to dumping it to stdout)

    -p/--param_file
        Provides a JSON file to load the executable arguments from'''
        )
        return RottnestMPIArgs.STATE_CLOSED_HELP


    def __init__(self):
        self.output_file = None
        self.param_file = None
        self.modules_to_load = set()

        self.outstanding_attributes = [ "architecture_name", "executable_name", "layout_file" ]
        self.attributes = dict()

        self.state = RottnestMPIArgs.STATE_OPEN
        self.error_msg = ""
        self.back_arg = ""


    def parse(self, arg):
        self.state = self.state(self, arg)


    def finalise(self) -> bool:
        if self.state is RottnestMPIArgs.STATE_CLOSED_HELP:
            return False

        if not self.state.final:
            # We hit an error and closed early
            if self.state is RottnestMPIArgs.STATE_CLOSED:
                perror(self.error_msg)
            else:
                perror(f"Arguments ended while expecting an additional argument for flag '{self.back_arg}'")
            return False
        elif self.outstanding_attributes:
            perror(f"No {self.outstanding_attributes.pop(0)} was provided")
            return False

        return True


    def get_arch_name(self):
        return self.attributes["architecture_name"]

    def get_exe_name(self):
        return self.attributes["executable_name"]

    def get_layout_file(self):
        return self.attributes["layout_file"]

    def get_output_file(self):
        return self.output_file

    def get_param_file(self):
        return self.param_file

    def get_modules(self):
        return self.modules_to_load


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
            tuple(id for id in layouts.keys()),
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
        # TODO : This should handle the queued items properly?
        # Alternatively, is this ok to just flush (or even not populate in the first place?)
        pool_completion_queue.get()

    # TODO : This works, but there might be a neater way to get the final result
    return pool_manager.composer.get_result().serialise()


def worker_main(comm, architecture, layouts, priority=False):
    '''
        Main function for the worker process(es)
    '''
    worker = architecture.worker()
    queue = MPIClientQueue(comm, priority=priority)

    # Queue is two way, and so is used for both tasks in and results out
    worker.main(queue, queue)


def main(architecture_name, executable_name, layouts, executable_params=None):
    '''
        Handles common behaviour before diverging to root/worker behaviour
    '''
    comm = MPI.COMM_WORLD

    # Load arch, exe and layouts
    architectures.set_current_architecture(architecture_name)
    executables.set_current_executable(executable_name)

    if executable_params is not None:
        executables.set_executable_params(**executable_params)

    architecture = architectures.get_current_architecture()
    executable = executables.get_current_executable()

    for layout_id, layout in layouts.items():
        LayoutProxy.add_layout_with_id(layout_id, layout)

    if comm.Get_rank() == 0:
        return root_main(comm, architecture, executable, layouts)
    else:
        worker_main(comm, architecture, layouts, priority = (comm.Get_rank() == comm.Get_size() - 1))
        return None
    #print(f"MPI peer {comm.Get_rank()} completed")


def launch():
    '''
        Handles arg parsing before delegating to main
    '''
    argv = sys.argv[1:]

    # Parse args
    args = RottnestMPIArgs.from_args(*argv)

    if args is None:
        exit(1)

    arch_name = args.get_arch_name()
    exe_name = args.get_exe_name()
    layout_file = args.get_layout_file()
    output_file = args.get_output_file()
    param_file = args.get_param_file()
    target_modules = args.get_modules()

    # For now, panic if there are not enough peers
    if MPI.COMM_WORLD.Get_size() < 3:
        print("rottnest_mpi requires at least three MPI peers to function")
        exit(1)

    # Silence stdout (TEMP : waiting for silencing internally of output)
    saved_stdout = sys.stdout
    dummy_writer_cls = type("DummyWriter", (), dict(write=lambda *a, **ka: None, flush=lambda *a, **ka: None))
    sys.stdout = dummy_writer_cls()
    sys.stderr = dummy_writer_cls()

    architectures.load_modules_from_strings(*target_modules)
    executables.load_modules_from_strings(*target_modules)


    # Open layout file and load layout
    # (currently single layout only, no validation)
    layouts = None
    try:
        with open(layout_file, 'r') as lf:
            layout_data = lf.read()

            layouts = {0: json.loads(layout_data)}
    except Exception as e:
        print(f"Failed to load file '{layout_file}' : {e}")
        exit(1)

    # If given, open and load parameters
    executable_params = None
    if param_file is not None:
        try:
            with open(param_file, 'r') as pf:
                param_data = pf.read()

                executable_params = json.loads(param_data)
        except Exception as e:
            print(f"Failed to load file '{layout_file}' : {e}")
            exit(1)


    # Run main - workers return None, root returns the final result
    res = main(arch_name, exe_name, layouts, executable_params)

    if res is not None:
        if output_file is None:
            print(res, file=saved_stdout)
        else:
            with open(output_file, "w") as f:
                print(res, file=f)


if __name__ == "__main__":
    launch()

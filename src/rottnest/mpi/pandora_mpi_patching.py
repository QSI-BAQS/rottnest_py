'''
    An MPI wrapper on pandora, so that worker interactions with
    pandora are mediated via MPI rather than attempting a direct connection
'''

from pandora.qualtran_to_pandora_util import windowed_cirq_to_pandora
from pandora.connection_util import insert_single_batch
from pandora.targeted_decomposition import add_cache_db

from rottnest.pandora.pandora_cache import pandora_cache, PandoraCache

from rottnest.pandora import pandora_connection

'''
    TODO
        - This should probably be unified under some standard protocol (especially if
          we may need to add new pandora functionality)
        - Unsure about sizes (1. bottleneck on network, 2. may be non-viable if massive)
        - Needs proper testing with an example that heavily uses pandora (cache requests, etc.)
'''


# Tags : Disjoint communication channels for different types of messages
TAG_PANDORA_TASK = 100
TAG_PANDORA_RESULT = 101

# Tasks : Minimum set that is actually used by rottnest
TASK_HALT = "HALT"
TASK_SPAWN = "SPAWN"
TASK_WIDGETIZE = "WIDGETIZE"
TASK_ADD_CACHE = "ADD_CACHE"


def mpi_pandora_cache_dispatch(op, do_hash=False, hash_override=None, *args, **kwargs):
    # NOTE : This will fail with a real pandora connection
    return pandora_connection.conn.mpi_add_cache(op, do_hash, hash_override, *args, **kwargs)


def mpi_patch_pandora_cache():
    pandora_cache.enable_cache_dispatch(mpi_pandora_cache_dispatch)


class MPIPandoraRootConnection():
    '''
        This object serves as a duck-typed Pandora object (where calls are dispatched
        rather than being handled locally)

        Note that the duck-typing is minimised to the set of functions actually used by Rottnest

        This object is only available to the root MPI node
    '''
    def __init__(self, comm, allocated_clients, decomp_window_size=10000):
        self.comm = comm
        self.rank = comm.Get_rank()

        if self.rank != 0:
            raise Exception("MPI Pandora connection is reserved for the MPI root peer")

        self.all_clients = allocated_clients.copy()

        self.db_allocation_idx = 0

        self.decomposition_window_size = decomp_window_size

        # Mapping of previously spawned tables to the client with that table
        self.tables = dict()


    def halt(self):
        for rank in self.all_clients:
            self.comm.send((TASK_HALT, tuple()), dest=rank, tag=TAG_PANDORA_TASK)


    def mpi_add_cache(self, op, do_hash=False, hash_override=None, *args, **kwargs):
        client_rank = self.all_clients[self.db_allocation_idx]
        self.db_allocation_idx = (self.db_allocation_idx + 1) % len(self.all_clients)

        # Send task
        self.comm.send(
            (
                TASK_ADD_CACHE,
                (
                    op,
                    args,
                    kwargs,
                    do_hash,
                    hash_override
                )
            ),
            dest=client_rank,
            tag=TAG_PANDORA_TASK
        )

        # Get early response
        table_name, res_v = self.comm.recv(source=client_rank, tag=TAG_PANDORA_RESULT)

        self.tables[table_name] = client_rank

        return (table_name, res_v)


    # --- Pandora Ducktyped Interface ---
    def spawn(self, database):
        # Handle case where we are re-spawning a table
        if database in self.tables:
            return MPIPandoraDBConnection(self.comm, self, database, self.tables[database])

        # Otherwise, ask a client to spawn the new table
        client_rank = self.all_clients[self.db_allocation_idx]
        # Tell the chosen client to spawn the database
        self.comm.send((TASK_SPAWN, (database,)), dest=client_rank, tag=TAG_PANDORA_TASK)

        self.db_allocation_idx = (self.db_allocation_idx + 1) % len(self.all_clients)

        return MPIPandoraDBConnection(self.comm, self, database, client_rank)


    def get_connection(self, database=None):
        raise NotImplementedError("MPI pandora remote connection cannot directly expose the database connection")


    def widgetize(self, max_t, max_d, batch_size, add_gin_per_widget):
        raise NotImplementedError("The root MPI pandora connection does not handle a widgetizable database")


    def build_pyliqtr_circuit(self, *_):
        raise NotImplementedError("MPI-based Pandora requires a patching over add_cache_db, to ensure build_pyliqtr_circuit is never invoked on the root side")



class MPIPandoraDBConnection():
    '''
        A single connection to a given database
    '''
    def __init__(self, comm, root, database, client_rank):
        self.comm = comm
        self.database = database
        self.client_rank = client_rank
        self.root = root

        # TEMP : Identify where manager-side code will attempt to use a now inaccessible
        # connection object
        self.connection = type("MPIPandoraMockConnection", tuple(), dict(
            close=lambda *a, **ka: None,
        ))

        self.decomposition_window_size = root.decomposition_window_size


    def mpi_add_cache(*args, **kwargs):
        # Delegate to root
        return self.root.mpi_add_cache(*args, **kwargs)


    def spawn(self, database):
        # Spawn requests propagate upwards to the root
        return self.root.spawn(database)


    def widgetize(self, max_t, max_d, batch_size, add_gin_per_widget):
        # Dispatch widgetisation job
        self.comm.send(
            (
                TASK_WIDGETIZE,
                (
                    self.database,    # We need to tell the client which database we are acting over
                    max_t,
                    max_d,
                    batch_size,
                    add_gin_per_widget
                )
            ),
            rank = self.client_rank,
            tag = TAG_PANDORA_TASK
        )

        # Stream the result from the client (yielding each individual widget)
        while True:
            # TODO : May need to be a stream of the widget list as well?
            widget_status, widget = self.comm.recv(source=self.client_rank, tag=TAG_PANDORA_RESULT)
            if not widget_status:
                break

            yield widget


    def build_pyliqtr_circuit(self, *_):
        raise NotImplementedError("MPI-based Pandora requires a patching over add_cache_db, to ensure build_pyliqtr_circuit is never invoked on the root side")


class MPIPandoraWorker():
    '''
        Provides the behaviour for a pandora worker node
    '''
    def __init__(self, comm, pandora_connection):
        self.comm = comm

        if self.comm.Get_rank() == 0:
            raise Exception("MPI pandora worker should not be running on the root peer")

        self.running = True

        self.pandora = pandora_connection

        self.databases = dict()

        self.task_handlers = {
            TASK_HALT: self.handle_task_halt,
            TASK_SPAWN: self.handle_task_spawn,
            TASK_WIDGETIZE: self.handle_task_widgetize,
            TASK_ADD_CACHE: self.handle_task_add_cache
        }


    def main(self):
        while self.running:
            # Get a task
            task, args = self.comm.recv(source = 0, tag=TAG_PANDORA_TASK)

            if task not in self.task_handlers:
                print(f"Got unknown task {task}")
            else:
                self.task_handlers[task](*args)


    def handle_task_halt(self, *args):
        self.running = False


    def handle_task_spawn(self, database, *args):
        # Spawn and track a new pandora connection to the given database
        conn = self.pandora.spawn(database)
        self.databases[database] = conn


    def handle_task_widgetize(self,
                              database,
                              max_t,
                              max_d,
                              batch_size,
                              add_gin_per_widget,
                              *args):
        # Cover case where an invalid database is requested
        # (terminate stream immediately so root doesn't hang)
        if database not in self.databases:
            self.comm.send((False, None), dest=0, tag=TAG_PANDORA_RESULT)
            return

        conn = self.databases[database]
        for wid in conn.widgetize(max_t, max_d, batch_size, add_gin_per_widget):
            # TODO : Could these be too big to send? May need to stream widget components
            self.comm.send((True, wid), dest=0, tag=TAG_PANDORA_RESULT)

        # Terminate the stream of widgets
        self.comm.send((False, None), dest=0, tag=TAG_PANDORA_RESULT)


    def handle_task_add_cache(self, op, args, kwargs, do_hash, hash_override):
        # Create the circuit
        circuit = op(*args, **kwargs)

        if hash_override is not None:
            table_name = hash_override
        else:
            table_name = PandoraCache.db_table_name(circuit, hash_postfix=do_hash)

        if do_hash:
            if hash_override is None:
                hsh = circuit._rottnest_hash()
            else:
                hsh = hash_override

            self.comm.send((table_name, hsh), dest=0, tag=TAG_PANDORA_RESULT)
        else:
            self.comm.send((table_name, type(circuit)), dest=0, tag=TAG_PANDORA_RESULT)

        add_cache_db(self.pandora, circuit, table_name)

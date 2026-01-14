'''
    An MPI wrapper on pandora, so that worker interactions with
    pandora are mediated via MPI rather than attempting a direct connection
'''

from pandora.qualtran_to_pandora_util import windowed_cirq_to_pandora
from pandora.connection_util import insert_single_batch
from pandora.targeted_decomposition import add_cache_db

from rottnest.pandora.pandora_cache import pandora_cache, PandoraCache

from rottnest.pandora import pandora_connection


# Tags for distinct channels
# NOTE : Other tags are present in mpi_queue
TAG_PANDORA_TASK = 100
TAG_PANDORA_RESULT = 101

# Tasks
# NOTE : Only the set of Pandora functions actually called in rottnest code are provided
# NOTE : Must be serializable and have <serialized remote instance> == <local instance>
TASK_HALT = "HALT"
TASK_SPAWN = "SPAWN"
TASK_WIDGETIZE = "WIDGETIZE"
TASK_ADD_CACHE = "ADD_CACHE"


def mpi_pandora_cache_dispatch(op, do_hash=False, hash_override=None, *args, **kwargs):
    '''
        Trivial dispatch method matching the signature required by pandora_cache,
        to be enabled as the cache dispatch method
    '''
    # NOTE : This call will fail with a real pandora connection object
    return pandora_connection.conn.mpi_add_cache(op, do_hash, hash_override, *args, **kwargs)


def pandora_patch_mpi(comm, allocated_ranks):
    '''
        Patches over current pandora connection with an MPI-based connection
        that dispatches pandora calls to MPI peers

        Should only be called on the MPI root, as worker nodes don't need pandora at all,
        and pandora nodes need an actual pandora connection

        comm provides the MPI communicator in use, and allocated_nodes is a list
        of ranks for clients that are to be sent pandora jobs
    '''
    # Patch over caching to dispatch cache additions
    pandora_cache.enable_cache_dispatch(mpi_pandora_cache_dispatch)

    # Patch over the pandora connection object itself
    pandora_connection.conn = MPIPandoraRootConnection(
        comm, allocated_ranks
    )


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
        # Get the next client peer
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

        # Get early response providing the chosen table name and either the hash or class
        # for the corresponding cache bind
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

        # spawn() is expected to provide another Pandora instance
        # instead, this provides a similar mock connection that tracks an associated database
        # and allows widgetisation
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

        # TODO : We may need some way to close older connections
        # to ensure Postgres doesn't reject further connections
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
        # NOTE : This defers the initial opening/creation of the database to
        # the first time it is used
        conn = PandoraConnectionWrapper(database)
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
        for wid in conn.get_connection().widgetize(max_t, max_d, batch_size, add_gin_per_widget):
            # TODO : Could these be too big to send? May need to stream widget components
            self.comm.send((True, wid), dest=0, tag=TAG_PANDORA_RESULT)

        # Terminate the stream of widgets
        self.comm.send((False, None), dest=0, tag=TAG_PANDORA_RESULT)

        # Close the connection to avoid hitting pg connection limits
        conn.close()


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


class PandoraConnectionWrapper():
    '''
        A wrapper on a pandora connection that provides a means of closing
        and reopening the underlying Postgres connection
    '''
    def __init__(self, root, database):
        self.root = root
        self.database = database
        self.pandora_connection = None

    def get_connection(self):
        if self.pandora_connection is not None:
            return self.pandora_connection

        self.pandora_connection = self.root.spawn(self.database)
        return self.pandora_connection

    def close(self):
        if self.pandora_connection is not None:
            self.pandora_connection.close()
            self.pandora_connection = None

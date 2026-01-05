'''
    An MPI wrapper on pandora, so that worker interactions with
    pandora are mediated via MPI rather than attempting a direct connection
'''

from pandora.qualtran_to_pandora_util import windowed_cirq_to_pandora
from pandora.connection_util import insert_single_batch

from mpi_uniq_tag import get_uniq_tag


'''
    TODO
        - This should probably be unified under some standard protocol (especially if
          we may need to add new pandora functionality)
        - Unsure about sizes (1. bottleneck on network, 2. may be non-viable if massive)
        - Needs proper testing with an example that heavily uses pandora (cache requests, etc.)
'''


# Tags : Disjoint communication channels for different types of messages
TAG_PANDORA_TASK = get_uniq_tag()
TAG_PANDORA_RESULT = get_uniq_tag()

# Tasks : Minimum set that is actually used by rottnest
TASK_HALT = "HALT"
TASK_SPAWN = "SPAWN"
TASK_WIDGETIZE = "WIDGETIZE"
TASK_BUILD_PYLIQTR_CIRCUIT = "BUILD_PYLIQTR"


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

        self.available_clients = allocated_clients.copy()
        self.all_clients = allocated_clients.copy()

        self.decomposition_window_size = decomp_window_size


    def halt(self):
        for rank in self.all_clients:
            self.comm.send((TASK_HALT, tuple()), dest=rank, tag=TAG_PANDORA_TASK)


    # --- Pandora Ducktyped Interface ---
    def spawn(self, database):
        if self.available_clients:
            client_rank = self.available_clients.pop(0)
            # Tell the chosen client to spawn the database
            self.comm.send((TASK_SPAWN, (database,)), dest=client_rank, tag=TAG_PANDORA_TASK)
            response = self.comm.recv(source=client_rank, tag=TAG_PANDORA_RESULT)

            # Check response
            if not response:
                # TODO
                raise Exception(f"Peer failed to spawn database {database}")

            self.available_clients.append(client_rank)

            print("Prepared spawned connection")
            return MPIPandoraDBConnection(self.comm, self, database, client_rank)
        else:
            raise Exception(f"No peer to dispatch spawn of database {database} to")


    def get_connection(self, database=None):
        raise NotImplementedError("MPI pandora remote connection cannot directly expose the database connection")


    def widgetize(self, max_t, max_d, batch_size, add_gin_per_widget):
        raise NotImplementedError("The root MPI pandora connection does not handle a widgetizable database")


    def build_pyliqtr_circuit(self, pyliqtr_circuit):
        raise NotImplementedError("The root MPI pandora connection does not handle a circuit database")



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

        # Initial response should be (TASK_WIDGETIZE, True) to confirm successs
        response = self.comm.recv(source=self.client_rank, tag=TAG_PANDORA_RESULT)

        task, result = response

        if task != TASK_WIDGETIZE:
            raise Exception(f"Got incorrect response task : {task}")
        if not result:
            raise Exception(f"Error during widgetisation")

        # Stream the result from the client (yielding each individual widget)
        while True:
            widget_status, widget = self.comm.recv(source=self.client_rank, tag=TAG_PANDORA_RESULT)
            if not widget_status:
                break

            yield widget


    def build_pyliqtr_circuit(self, pyliqtr_circuit):
        # Decomposition into serialisable pandora gates occurs on the root side
        # as pyliqtr circuits are not generally serialisable
        batches = windowed_cirq_to_pandora(circuit=pyliqtr_circuit,
                                           window_size=self.decomposition_window_size)

        # Initialise build
        self.comm.send(
            (
                TASK_BUILD_PYLIQTR_CIRCUIT,
                (self.database,)        # As above, need to inform the client of the database in use
            ),
            dest=self.client_rank,
            tag=TAG_PANDORA_TASK
        )

        response = self.comm.recv(source=self.client_rank, tag=TAG_PANDORA_RESULT)

        # Initial response should be (TASK_BUILD_PYLIQTR_CIRCUIT, True) to confirm
        task, result = response

        if task != TASK_BUILD_PYLIQTR_CIRCUIT:
            raise Exception(f"Got incorrect response task : {task}")
        if not result:
            raise Exception(f"Error during circuit building")

        # Dispatch each batch to the client
        for batch, decomp_time in batches:
            self.comm.send(
                (
                    TASK_BUILD_PYLIQTR_CIRCUIT,
                    batch
                ),
                dest=self.client_rank,
                tag=TAG_PANDORA_TASK
            )

        # End the batches
        self.comm.send(
            (
                TASK_BUILD_PYLIQTR_CIRCUIT,
                None
            ),
            dest=self.client_rank,
            tag=TAG_PANDORA_TASK
        )


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
            TASK_BUILD_PYLIQTR_CIRCUIT: self.handle_task_build_pyliqtr
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

        # Confirm the spawn
        self.comm.send(True, dest=0, tag=TAG_PANDORA_RESULT)


    def handle_task_widgetize(self,
                              database,
                              max_t,
                              max_d,
                              batch_size,
                              add_gin_per_widget,
                              *args):
        if database not in self.databases:
            print(f"Got unknown database {database} for widgetize")
            self.comm.send((TASK_WIDGETIZE, False), dest=0, tag=TAG_PANDORA_RESULT)
            return

        # Open the stream of widgets
        self.comm.send((TASK_WIDGETIZE, True), dest=0, tag=TAG_PANDORA_RESULT)

        conn = self.databases[database]
        for wid in conn.widgetize(max_t, max_d, batch_size, add_gin_per_widget):
            # TODO : Could these be too big to send?
            self.comm.send((True, wid), dest=0, tag=TAG_PANDORA_RESULT)

        # Terminate the stream of widgets
        self.comm.send((False, None), dest=0, tag=TAG_PANDORA_RESULT)


    def handle_task_build_pyliqtr(self, database, *args):
        '''
            We can't serialise arbitrary pyliqtr objects

            However, we can process them on the manager side,
            and stream the resulting Pandora gates, essentially
            recreating build_pyliqtr_circuit, just disjoint between
            two nodes
        '''
        if database not in self.databases:
            print(f"Got unknown database {database} for build_pyliqtr_circuit")
            self.comm.send((TASK_BUILD_PYLIQTR_CIRCUIT, False), dest=0, tag=TAG_PANDORA_RESULT)
            return

        conn = self.databases[database]

        # Confirm start of build
        self.comm.send((TASK_BUILD_PYLIQTR_CIRCUIT, True), dest=0, tag=TAG_PANDORA_RESULT)

        conn.build_pandora()

        # Stream pandora gates representing the pyliqtr circuit
        task, batch = self.comm.recv(source=0, tag=TAG_PANDORA_TASK)

        while batch is not None:
            if task != TASK_BUILD_PYLIQTR_CIRCUIT:
                print(f"Got bad task {task} during stream of pyliqtr gates")
                return

            insert_single_batch(connection=conn.connection, batch=batch)

            task, batch = self.comm.recv(source=0, tag=TAG_PANDORA_TASK)

        conn.build_edge_list()



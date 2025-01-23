import multiprocessing as mp
from threading import Thread
from typing import Any
from rottnest.compute_units.compute_unit import ComputeUnit 
from rottnest.widget_compilers.main import run as run_widget


def run_sequence_elem(args):
    compute_unit, arch_obj = args
    compute_unit: ComputeUnit
    print("running elem")
    # TODO replace with actual impl + add try/except
    try:
        widget = compute_unit.compile_graph_state()
        print("compile done")
        orch = run_widget(cabaliser_obj=widget.json(), region_obj=arch_obj)
        print("execution done")
        print("ST volume:", orch.get_space_time_volume())
        print("T source stats:", orch.get_T_stats())
        resp = orch.json
        print("returning result")
        return (False, resp)
    except Exception as e:
        import traceback
        tb = traceback.format_exception(e)
        return (True, {'err_type': repr(e), 'traceback': tb})

def task_run_sequence(arch_obj):
    # TODO farm off to actual code
    from rottnest.input_parsers.pyliqtr_parser import PyliqtrParser
    from rottnest.input_parsers.cirq_parser import CirqParser
    from rottnest.compute_units.sequencer import Sequencer

    # pyLIQTR 1.3.3
    from pyLIQTR.ProblemInstances.getInstance import getInstance
    from pyLIQTR.clam.lattice_definitions import SquareLattice, TriangularLattice
    from pyLIQTR.BlockEncodings.getEncoding import getEncoding, VALID_ENCODINGS
    from pyLIQTR.qubitization.qsvt_dynamics import qsvt_dynamics, simulation_phases
    from pyLIQTR.qubitization.qubitized_gates import QubitizedWalkOperator
    from pyLIQTR.circuits.operators.AddMod import AddMod as pyLAM

    # https://github.com/isi-usc-edu/qb-gsee-benchmark, commit 4c547e8
    from qb_gsee_benchmark.qre import get_df_qpe_circuit
    from qb_gsee_benchmark.utils import retrieve_fcidump_from_sftp

    # pyscf v2.7.0
    from pyscf  import ao2mo, tools

    # openfermion v1.6.1
    from openfermion import InteractionOperator

    from pyLIQTR.utils.circuit_decomposition import circuit_decompose_multi

    print("import done")

    def make_qsvt_circuit(model,encoding,times=1.0,p_algo=0.95):
        """Make a QSVT based circuit from pyLIQTR"""
        eps = (1 - p_algo) / 2
        scaled_times = times * model.alpha
        phases = simulation_phases(times=scaled_times, eps=eps, precompute=False, phase_algorithm="random")
        gate_qsvt = qsvt_dynamics(encoding=encoding, instance=model, phase_sets=phases)
        return gate_qsvt.circuit
    def make_fh_circuit(N=2, times=1.0, p_algo=0.95):
        """Helper function to build Fermi-Hubbard circuit."""
        # Create Fermi-Hubbard Instance
        J = -1.0
        U = 2.0
        model = getInstance("FermiHubbard", shape=(N, N), J=J, U=U, cell=SquareLattice)
        return make_qsvt_circuit(model,encoding=getEncoding(VALID_ENCODINGS.PauliLCU),times=times,p_algo=p_algo)
    
    N = 2
    fh = make_fh_circuit(N=N,p_algo=0.9999999904,times=0.01)
    parser = PyliqtrParser(fh)
    parser.parse()
    seq = Sequencer(None)


    # Actual work here.
    it = seq.sequence_pyliqtr(parser)
    task_work_fn = run_sequence_elem
    task_args_additional = (arch_obj,)

    print("circuit done")
    return (it, task_work_fn, task_args_additional)

operation_map = {"task_run_sequence": task_run_sequence}


class AsyncIteratorProcessPool:    
    @staticmethod
    def _manager_main(task_queue: mp.Queue, completion_queue: mp.Queue, completion_callback: Any):
        print("in manager main")
        pool = mp.Pool(processes=1)

        while True:
            task_name, *args = task_queue.get()

            print("got task", task_name)

            if task_name == 'terminate':
                break
            
            it, work_fn, work_args = operation_map[task_name](*args)

            wrapped_iter = ((obj, *work_args) for obj in it)

            def wrapped_iter_test(it):
                for i, obj in enumerate(it):
                    if i > 0:
                        break
                    yield (obj, *work_args)

            for (is_err, payload) in pool.imap_unordered(work_fn, wrapped_iter_test(it)):
                s = str(payload)
                if not is_err: # Always print full errors
                    s = s[:min(200, len(s))]

                    print("pool completed", s)
                else:
                    print("pool completed err:")
                    print(''.join(payload['traceback']))
                completion_callback(payload, err=is_err)

        pool.terminate()

    def __init__(self, completion_callback):
        self.task_queue = mp.Queue()
        self.manager = Thread(target=self._manager_main, args=[self.task_queue, None, completion_callback])
        self.manager.start()
        print("init done")
        # TODO delete, we don't need this field
        self.completion_callback = completion_callback

    def pool_submit(self, task_name, *args):
        if task_name == "debug":
            class Debug:
                def compile_graph_state(self):
                    class Debug2:
                        def json(self):
                            return {
                                "n_qubits": 4,
                                "consumptionschedule": [[{0: []}], [{1: [0]}], [{2: [1]}], [{3: [2]}]],
                                "adjacencies": {0: [1], 1: [0], 2: [3], 3: [2]}
                            }
                    return Debug2()
            (is_err, payload) = run_sequence_elem((Debug(), args[0]))
            if is_err:
                print("err", payload)
            self.completion_callback(payload, err=is_err)
            return
        self.task_queue.put((task_name, *args))

    def terminate(self):
        self.task_queue.put(('terminate', ))
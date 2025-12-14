import unittest
import random


class T_RZ_Test(unittest.TestCase):
   
    def rz_cirq_circuit(self, n_qubits=3, n_rz_gates=100, rads=0.01):
        import cirq

        qubits = cirq.LineQubit.range(n_qubits)

        circ = cirq.Circuit()  


        rz = cirq.Rz(rads=rads) 

        for i in range(n_rz_gates): 
            targ = qubits[random.randint(0, n_qubits - 1)]

            circ.append(rz(targ))
            circ.append(cirq.X(targ))


        from rottnest.executables.t_rz_executable import T_RZ_RottnestExecutable 
        class Exec(T_RZ_RottnestExecutable):
            @classmethod
            def get_parameters(cls):
                return {}
        
            def _generate_circuit(self, *args, **kwargs):
                return self._circ
        Exec._circ = circ

        return Exec 


    def rz_qualtran_circuit_from_cirq(self, *args, **kwargs):

        from qualtran import CompositeBloq 


        executable = self.rz_cirq_circuit(*args, **kwargs) 
        cirq_circuit = executable._circ 
        qualtran_circuit = CompositeBloq.from_cirq_circuit(cirq_circuit) 
        executable._circ = qualtran_circuit


        def cbloq_iter(self): 
            '''
            Dodgy out of order iterator
            '''
            for i in self.bloq_instances:
                yield i.bloq.as_cirq_op()

        CompositeBloq.__iter__ = cbloq_iter 

        return executable

  
    def test_rz_count_cirq(self):
  
        n_rz_gates = 100 
        executable = self.rz_cirq_circuit(n_qubits = 1, n_rz_gates=n_rz_gates) 
        
        # Check that no gates decomposed
        assert len(executable._circ) == 2 * n_rz_gates 

        assert executable().n_rz() == n_rz_gates

    def test_rz_count_cirq_multi_target(self):
  
        n_rz_gates = 300 
        executable = self.rz_cirq_circuit(n_qubits = 3, n_rz_gates=n_rz_gates) 
        
        # Check that no gates decomposed
        assert len(executable._circ) < n_rz_gates 

        assert executable().n_rz() == n_rz_gates


    def test_rz_count_qualtran_via_pyliqtr(self):
        n_rz_gates = 7

        from pyLIQTR.utils.circuit_decomposition import circuit_decompose_multi, generator_decompose 
        executable = self.rz_qualtran_circuit_from_cirq(n_qubits=1, n_rz_gates=n_rz_gates)         

        cirq_circuit = generator_decompose(executable()._generate_circuit()) 
        for i in cirq_circuit: 
            print(i)

if __name__ == '__main__':
    tst = T_RZ_Test()
    tst.test_rz_count_qualtran_via_pyliqtr()


        

import Quantum.Synthesis.GridSynth
import Quantum.Synthesis.SymReal
import Quantum.Synthesis.CliffordT
import System.Random
import System.IO
import Quantum.Synthesis.Ring
import Quantum.Synthesis.Ring.FixedPrec()
import Quantum.Synthesis.Matrix
import Quantum.Synthesis.GridProblems
import Quantum.Synthesis.Diophantine
import Quantum.Synthesis.StepComp
import Quantum.Synthesis.QuadraticEquation

phase_gridsynth :: (RandomGen g) => g -> Double -> SymReal -> Int -> U2 DOmega
phase_gridsynth g prec theta effort = m where
  (m, _, _) = gridsynth_phase_stats g prec theta effort

phase_gridsynth_gates :: (RandomGen g) => g -> Double -> SymReal -> Int -> [Gate]
phase_gridsynth_gates g prec theta effort = synthesis_u2 (phase_gridsynth g prec theta effort)


gate_synth :: IO ()
gate_synth = do
    input <- getLine
    let (p:q:precision:effort:seed:xs) = map read(words input) :: [Int]

    let angle = ( Pi * to_real p ) / to_real q

    print(phase_gridsynth_gates(mkStdGen seed)(fromIntegral precision)(angle)(effort))

    gate_synth

main :: IO ()
main = do 
    hSetBuffering stdout NoBuffering
    gate_synth
    

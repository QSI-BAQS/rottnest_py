from ejc.executable import EJCSchrodinger, EJCInteraction 


delta = 1e-2
omega_atom = 1e3
omega_photon = omega_atom + delta 
gamma_max = 1

current_executable = EJCInteraction(
    70,
    7,
    omega_atom = omega_atom,
    omega_photon=omega_photon,
    gamma_max=gamma_max,
    epsilon_target=0.01,
)

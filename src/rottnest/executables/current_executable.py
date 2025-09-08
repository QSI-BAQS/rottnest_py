from ejc.executable import EJC, EJCInteraction 

current_executable = EJC(
    20,
    4,
    epsilon_target=0.25,
    omega = 1e-2,
    delta = 1e-2 - 1e-3
)

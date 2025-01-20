def t_orchestration(t_orc, prewarm_cycles: int = 0):
    
    # Prewarm the scheduler
    t_orc.prewarm(prewarm_cycles)

    # Run the scheduler
    t_orc.schedule()
    return

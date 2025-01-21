def t_orchestration(t_orc, prewarm_cycles: int = 0):
    
    # Run the scheduler
    t_orc.schedule()
    return

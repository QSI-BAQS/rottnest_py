from rottnest.compute_units import compute_unit
from rottnest.shared_rng import SharedRNG

from t_scheduler.templates.generic_templates import LayoutNode
from t_scheduler.widget.widget_region import RegionStats 

'''
    Superconducting class
    Compositional class wrapping the t_scheduler and compute units 
'''

class Superconducting(compute_unit.ComputeUnit, SharedRNG):
    def __init__(self, 
        bell_rate: float, 
        layout: LayoutNode,
        generator: SharedRNG = None,
        seed: int = 0):

        SharedRNG.__init__(self, generator=generator, seed=seed) 
        self.layout = layout
        
        # Generate the layout
        regions, routers = layout.create()

        self.regions = regions
        self.routers = routers
        
        stats = sum((region.stats for region in regions), start=RegionStats())
        self.stats = stats

        self.bell_rate = bell_rate
        self.num_registers = stats.num_registers  
        self.num_t_buffers = stats.num_t_buffers
        self.num_bell_buffers = stats.num_bell_buffers

        # Calc T rate
        self.t_rate = self.simulate_t_rate()   

    def simulate_t_rate(self, n_pre_warm_cycles=0):
        n_cycles = self.stage_1() + self.stage_2()
        t_count = estimate_generated_t_count(self.layout, n_cycles + n_pre_warm_cycles) 
        return t_count / n_cycles 

    def profile_t_rate(self, n_reps=100):
        # TODO
        pass

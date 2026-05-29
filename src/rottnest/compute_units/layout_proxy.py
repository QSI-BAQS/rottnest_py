'''
    Proxy class for managing layouts
'''
from typing import Generator

class LayoutProxy:
    '''
        This class does an interesting double shift
        The first is as an interface for a singleton cache
        of saved layouts
        The second is as an interface wrapper for the json
        object stored in the cache, with a particular
        emphasis in providing a translation layer for
        the composer

        Architecture load will trigger a monkeypatch
         on the instance of this class in the current
         process

        This generic form is exposed to the workers
    '''

    # Singleton layout cache
    curr_layout_id = 0

    # Singleton json cache
    saved_layouts = {}

    # Singleton proxy cache
    saved_proxies = {}

    @classmethod
    def add_layout(cls, layout):
        '''
            Adds a layout, id is incremented
            Should be used as a single source of truth, then ids
             passed to subprocesses
            `curr_layout_id` is not guaranteed to be synchronous
             between processes
        '''
        layout_id = cls.curr_layout_id
        cls.saved_layouts[layout_id] = layout
        cls._refresh_proxy_by_id(layout_id)
        cls.curr_layout_id += 1
        return layout_id

    @classmethod
    def add_layout_with_id(cls, layout_id, layout):
        '''
            Binds a layout to a given id
            Should be used for
        '''
        cls.saved_layouts[layout_id] = layout
        cls._refresh_proxy_by_id(layout_id)


    @classmethod
    def _refresh_proxy_by_id(cls, layout_id):
        '''
            Refresh to avoid membound lingering from previous
            architecture
        '''
        if layout_id in cls.saved_proxies:
            cls.saved_proxies[layout_id].refresh_mem_bound()

    @classmethod
    def force_proxy_refresh(cls):
        '''
            Force a refresh of membounds for every saved proxy
        '''
        for layout in cls.saved_proxies.values():
            layout.refresh_mem_bound()

    @classmethod
    def get_layouts(cls) -> Generator:
        '''
            Gets all layouts
        '''
        return cls.saved_layouts.items()

    @classmethod
    def flush(cls):
        '''
            Flushes all saved layouts
            Returns the layouts
        '''
        layouts = cls.saved_layouts

        cls.curr_layout_id = 0
        cls.saved_layouts = {}
        cls.saved_proxies = {}
        return layouts


    @classmethod
    def reload_layouts(cls, layouts):
        '''
            Reloads a collection of layouts
        '''
        for idx, layout in layouts.items():
            cls.add_layout_with_id(idx, layout)
        return

    @classmethod
    def get_layout(cls, layout_id) -> dict:
        return cls.saved_layouts.get(layout_id, None)

    @classmethod
    def check_pregenerated(cls, layout_id):
        if layout_id not in cls.saved_layouts:
            raise ValueError(f"Unknown layout with id {layout_id}")
        return layout_id in cls.saved_proxies

    def __new__(cls, layout_id):
        if cls.check_pregenerated(layout_id):
            return cls.saved_proxies[layout_id]
        else:
            return object.__new__(LayoutProxy)

    def __init__(
        self,
        layout_id
        ):
        '''
            Compute Unit Constructor
            :: bell_rate : float :: Number of bell states generated per toc for one interface
            :: t_rate : float :: Average number of T states generated per toc
            :: reg_max : int :: Maximum number of allocatable registers
            :: t_buffer_max : int :: Maximum number of bufferable T states
            :: bell_buffer_max : int :: Maximum number of bufferable Bell states

            Given factory warm up times, t_rate should be calculated including the warm up period
            The rate should be calculated over the stage 1 and stage 2 times
            The rate should be capped at t_buffer_max

            TODO: More complex, but forward speculating some diminishing number of additional T
            gates generated during stage 3
        '''

        if self.check_pregenerated(layout_id):
            # Skip __init__, we returned an past generated object in __new__
            return

        # TODO: replace arch_id with layout_id

        self.layout_id = layout_id

        from rottnest.plugins import architectures
        arch_module = architectures.get_current_architecture()

        self.num_registers = arch_module.designer().get_mem_bound(
            self.to_json()
        )

        # Now that we've stolen the layout, save ourselves to the mapping
        LayoutProxy.saved_proxies[layout_id] = self

    def mem_bound(self):
        '''
            Maximum number of elements in the graph
        '''
        return self.num_registers

    def refresh_mem_bound(self):
        '''
            Recompute memory bound
            Required if arch_module has changed, otherwise the previous mem_bound will
            be used
        '''
        # Cursed, but also the way __init__ does it???
        from rottnest.plugins import architectures
        arch_module = architectures.get_current_architecture()

        self.num_registers = arch_module.designer().get_mem_bound(
            self.to_json()
        )

    def to_json(self):
        return LayoutProxy.get_layout(self.layout_id)

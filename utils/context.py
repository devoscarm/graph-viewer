class AppContext:
    '''
    For propagating application context and other utilities
    Can be modified during the runtime!
    '''
    def __init__(self, app, settings_manager):
        self.app = app
        self.settings_manager = settings_manager
        # I'll initialize them during the runtime
        self.window = None
        self.graph_area = None
        self.data_manager = None
        self.plot_manager = None
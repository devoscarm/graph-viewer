class AppContext:
    '''
    For propagating application context and other utilities
    Can be modified during the runtime!
    '''
    def __init__(self, app, settings_manager):
        # The app session that is running
        self.app = app
        # App defaults and last session configurations
        self.settings_manager = settings_manager
        # All the windows that will be opened
        self.windows = []
        

class WindowContext:
    '''
    Charatteristics to be propagated between elements
    of the same window
    '''
    def __init__(self, window):
        self.window = window
        self.graph_area = None
        self.data_manager = None
        self.plot_manager = None

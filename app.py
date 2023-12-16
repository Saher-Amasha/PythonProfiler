
import threading
from example_usage.example1 import Example
from profiler_server import ProfilerServer
from view.main_view import MainView


        
class app:
    server_instance = ProfilerServer()
    MainWindow = MainView()

    @staticmethod
    def run_test_mode():
        threading.Thread(target=app.server_instance.run).start()
        threading.Thread(target=Example.test).start()
        app.MainWindow.run()
    
    @staticmethod
    def run():
        threading.Thread(target=app.server_instance.run).start()
        app.MainWindow.run()
    
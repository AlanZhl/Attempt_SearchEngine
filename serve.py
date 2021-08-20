from app import create_app
from threads import ScrawlerThread
import os
import shutil


from app.config import Config


app = create_app()

if __name__ == "__main__":
    # # opt to start the multi-threaded job scrawler
    # mission1 = ScrawlerThread(keyword="software", driver="chrome", date=3)
    # mission2 = ScrawlerThread(keyword="IT", driver="firefox", date=3)

    # mission1.start()
    # mission2.start()
    
    # run the server instance (please close the debug mode when run with a scrawling process)
    app.run(debug = True, port = 9001)
from app import create_app
from threads import ScrawlerThread


app = create_app()

if __name__ == "__main__":
    # # opt to start the multi-threaded job scrawler
    # mission1 = ScrawlerThread(keyword="software", driver="chrome", date=7)
    # mission2 = ScrawlerThread(keyword="IT", driver="firefox", date=7)

    # mission1.start()
    # mission2.start()
    # mission1.join()
    # mission2.join()
    
    # run the server instance (please close the debug mode when run with a scrawling process)
    app.run(debug = False, host="0.0.0.0", port = 9001)
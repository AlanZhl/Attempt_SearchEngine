from app import create_app
from threads import ScrawlerThread
from save_samples import save_samples, load_samples


app = create_app()

if __name__ == "__main__":
    # # opt to start the multi-threaded job scrawler
    # mission1 = ScrawlerThread(keyword="software", driver="chrome", date=14)
    # mission2 = ScrawlerThread(keyword="IT", driver="firefox", date=14)

    # mission1.start()
    # mission2.start()
    # mission1.join()
    # mission2.join()

    # # opt to load samples from "samples.csv"
    # save_samples()
    load_samples()

    
    # run the server instance (please close the debug mode when run with a scrawling process)
    app.run(debug = False, host="0.0.0.0", port = 9001)
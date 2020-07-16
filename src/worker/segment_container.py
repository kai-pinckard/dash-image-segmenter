if __name__ == "__main__":
    import sys, getopt
    import imageio
    import numpy as np
    import os
    import json
    import requests
    import random
    import time
    from datetime import datetime
    from see import GeneticSearch, Segmentors
    #=====================================================================
    """
    Note: these are all the default values unless they are changed by
    a command line argument these values will hold.
    """

    # These values control the genetic search
    pop_size = 10
    num_gen = 5

    # These values describe wait times before image download attempts
    initial_delay = 5
    download_delay = 2

    # The url of the server to contact
    server_url = "http://0.0.0.0:8080"  

    # These are relative urls and must be combined with the server url
    rgb_url = "static/rgb.jpg"
    label_url = "static/label.jpg"

    """
    A consistent seed ensures repeatable results, but severely limits the search
    for a good segmentation algorithm. Using the seed parameter
    elimates any benefit from running multiple instances of this container.

    A seed is used no matter what value is used for the flags. The difference is that when -s
    is not specified the seed will be picked based on the current time. In contrast, when -s is
    specified a seed of 0 will always be used.

    The seed is a Work in Progress and is not yet functional.
    """
    seed = datetime.now()

    #=====================================================================
    # Handle command line arguments
    try:
        opts, args = getopt.getopt(sys.argv[1:], "p:g:l:hs")
    except getopt.GetoptError:
        print("For help run:")
        print("python segment_container.py -h")
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            print("flags:")
            print("l: Location")
            print("g: number of Generations")
            print("p: Population size")
            print("s: use a Seed for repeatable results")
            print("To run in a kubernetes cluster run:")
            print("python segment_container.py -l cluster")
            print("To run locally run:")
            print("python segment_container.py")
            print("To run with a population size of 6 and to simulate 7 generations run:")
            print("python segment_container.py -p 6 -g 7")
            print("To run locally with a seed run:")
            print("python segment_container.py -s")
            print("The defaults:")
            print("By default location=local population=10 generations=5 seed=False")
            sys.exit()
        elif opt == "-l":
            if arg == "cluster":
                server_url = "http://serverservice"
        elif opt == "-p":
            pop_size = int(arg)
        elif opt == "-g":
            num_gen = int(arg)
        elif opt == "-s":
            seed = 0
    print("Running with parameters:")
    print("population size =", str(pop_size))
    print("number of generations =", str(num_gen))
    print("server url =", server_url)
    print("seed =", seed)
    print("")

    print("Attempting to download images in", initial_delay, "second(s)")
    time.sleep(initial_delay)

    # Create image urls
    rgb_url = server_url + "/" + rgb_url
    label_url = server_url + "/" + label_url

    # Temporary, needs to be replaced with a means of determining the filetype
    rgb_filename = "rgb.jpg"
    label_filename = "label.jpg"

    # Create image download commands
    get_rgb = "wget -O " + str(rgb_filename) + " " + str(rgb_url)
    get_label = "wget -O " + str(label_filename) + " " + str(label_url)


    # Download the images
    download_status = os.system(get_rgb)
    download_status = download_status + os.system(get_label)

    while download_status != 0:
        print("Download failed retrying in", download_delay, "second(s)")
        time.sleep(download_delay)
        download_status = os.system(get_rgb)
        download_status = download_status + os.system(get_label)

    # Load the images
    img = imageio.imread(rgb_filename)
    gmask = imageio.imread(label_filename)

    # Only needed on some images
    # Convert the RGB 3-channel image into a 1-channel image
    # gmask = (np.sum(gmask, axis=2) > 0)

    # Create an evolver
    my_evolver = GeneticSearch.Evolver(img, gmask, pop_size=pop_size)
    
    # Conduct the genetic search
    population = None

    for i in range(num_gen):

        # if population is uninitialized
        if population is None:
            population = my_evolver.run(ngen=1)
        else:
            # Simulate a generation and store population in population variable
            population = my_evolver.run(ngen=1, population=population)

        # Take the best segmentor from the hof and use it to segment the rgb image
        seg = Segmentors.algoFromParams(my_evolver.hof[0])
        mask = seg.evaluate(img)

        # Calculate and print the fitness value of the segmentor
        fitness = Segmentors.FitnessFunction(mask, gmask)[0]
        params = my_evolver.hof[0]

        # Combine data into a single object
        data = {}
        data["fitness"] = fitness
        data["params"] = params

        # Convert the data to json format
        data = json.dumps(data)

        print(i, data, "\n\n")

        # Send data to web server
        server_update_url = server_url + "/update"
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        r = requests.post(server_update_url, data=json.dumps(data), headers=headers) 
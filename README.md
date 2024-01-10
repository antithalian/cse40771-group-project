# sPin - CSE 40771 Final Group Project
#### By John Sullivan and Jozef Porubcin
    
In order to run our system, your Python installation must have `aiohttp` and `requests` installed. All remaining required libraries (that aren't dependencies of those two) should already be present with your Python installation. We developed and tested our system using Python 3.9.16.

The main aspects of our system are contained in the `server` and `client` directories:
- `sPinClient.py`, found in the `client` directory, is both an RPC library and a CLI agent for interacting with our system (for an example of how to use it as an RPC library, see `test_performance.py` and the client's own main/CLI section.
  - When run with `help` as its argument or run incorrectly, `sPinClient.py` will give a help message on how to use it.
- `sPinServer.py` and associated files in `server` are not meant to be run directly from the top-level project directory, as they require a directory structure to be created for them for storing metadata and persisting data objects to disk.

To set up and run our system for testing, we recommend using the following process:
- run `python3 init/init_files.py` (optionally with an integer file size as the second argument) in order to initialize a directory containing 200 files of ~1MB by default. These will be located at `files/*` from the project root.
- run `python3 init/init_peers.py $NUM_PEERS` in order to initialize `$NUM_PEERS` peers. These will be placed in a `peers/*` directory off of the project root. Each peer will consist of a directory named with the peer's UUID, with the internal structure of that directory being the structure required by the peer server to run.
- enter each peer directory and run `python3 sPinServer.py` (we tested this by using `tmux` to have a number of shells to run the peers in, as our peer server prints output to show what's going on in the system)
  - the peers will quickly begin advertising themselves to the nameserver and communicating with each other
- use `python3 client/sPinClient.py $ARGS` to proceed with whatever operations on the system that you'd like to run!

Between runs of the peers, it may be helpful to run this command in each peer's directory: `rm meta/dels.log meta/pins.log meta/pins.ckpt; rm pinned_files/*; rm cached_files/*; cp ../../server/sPinServer.py . && python3 sPinServer.py`. Assuming you aren't trying to test what happens when peers come back up with their original data, that will clear everything out and make them act as if they are brand new. This avoids the annoyance of having to exit the peers directory, rerun the peer initialization script, and reenter under a new directory name for each peer you wish to run.

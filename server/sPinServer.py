#!/usr/bin/env python3

# John Sullivan (jsulli28), Jozef Porubcin (jporubci)
# sPinServer.py

import asyncio, aiohttp
from aiohttp import web
import socket # need constants
import uuid, json, os

import sys
import pprint # for debug

class sPinServer:

    # get DEBUG mode or not from env var
    DBG = True if int(os.getenv('DEBUG', default=0)) == 1 else False

    # time constants
    BASE_INTERVAL = 10
    # TODO: add others as multiples of base interval

    # nameserver constants
    NAMESERVER_NAME = 'catalog.cse.nd.edu'
    NAMESERVER_PORT = 9097
    NAMESERVER_URL = '/query.json'
    NAMESERVER_WAIT = BASE_INTERVAL * 6

    # project name for nameserver
    NAMESERVER_TYPE = 'sPin'
    NAMESERVER_OWNER = 'jsulli28/jporubci'

    # storage locations
    PIN_DIR = 'pins'
    CACHE_DIR = 'cache'
    # TODO: add checkpoint/log (YAML?)
    # needs to hold both deletions and $UUID-$HASH combos

    def __init__(self, id):

        # temporary UUID until we can store it
        self.uuid = id
        
        # $UUID-$HASH table
        # TODO: load from file w/ checkpoint/log (or maybe just from the pins dir?)
        self.identifiers = {fn : True for fn in os.listdir(self.PIN_DIR)}

        # deletion table
        # TODO: load from file w/ checkpoint/log
        self.deletions = {}

        # peers table - to be initialized at first run of retrieve
        self.peers = None
        # port - to be initialized when server initialized
        self.port = None

    # update nameserver
    async def update_nameserver(self):
        msg = {
            'type': self.NAMESERVER_TYPE,
            'owner': self.NAMESERVER_OWNER,
            'port': self.port,
            'uuid': self.uuid,
        }
        msg_encoded = json.dumps(msg).encode()

        # keep going forever
        while True:
            """# send message to the nameserver
            # TODO: try/except??? - can't find the exception we'd need to catch... don't want to just catch everything, that'd grab CTRL-C and stuff
            _, write = await asyncio.open_connection(self.NAMESERVER_NAME, self.NAMESERVER_PORT, family=socket.AF_INET, proto=socket.SOCK_DGRAM)

            if self.DBG: pprint.pprint(msg)

            write.write(msg_encoded)
            await write.drain()

            write.close()
            await write.wait_closed()"""

            if self.DBG: pprint.pprint(msg)

            # TODO: consider using the above async/await form of this... possibly unnecessary since it's a single, quick connection
            # send message, context handler to close
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
                # avoid setup, use sendto
                udp_socket.sendto(msg_encoded, (self.NAMESERVER_NAME, self.NAMESERVER_PORT))

            # wait the required amount of time
            await asyncio.sleep(self.NAMESERVER_WAIT)

    # retrieve from nameserver
    async def retrieve_peers(self):
        # keep going forever
        while True:

            # async retrieval of the JSON
            async with aiohttp.ClientSession() as session:
                async with session.get(f'http://{self.NAMESERVER_NAME}:{self.NAMESERVER_PORT}{self.NAMESERVER_URL}') as resp:
                    # TODO: error check
                    nameserver_json = await resp.json(content_type=None) # disable content type check, nameserver gives text even though it's json

            # find our project in nameserver json response
            # TODO: fix the fact that this will currently find a crapload of stuff if there's been a lot of churn at the nameserver recently
            #self.peers = [entry for entry in nameserver_json if entry.get('type', '') == self.NAMESERVER_TYPE and entry.get('uuid') != self.ID]
            all_peers = [entry for entry in nameserver_json if entry.get('type', '') == self.NAMESERVER_TYPE and entry.get('uuid') != self.uuid]

            if self.DBG: pprint.pprint(all_peers)

            duplicates = {}
            for peer in all_peers:
                if peer['uuid'] in duplicates:
                    duplicates[peer['uuid']].append(peer)
                else:
                    duplicates[peer['uuid']] = [peer]
            #print(duplicates)
            self.peers = [max(dupes, key=lambda k: k['lastheardfrom']) for dupes in duplicates.values()]
            print('received following peers:')
            pprint.pprint(self.peers)
            # broadcast to all peers
            await self.broadcast(self.peers)

            # wait the required amount of time
            await asyncio.sleep(self.NAMESERVER_WAIT)

    # broadcast information to other peers
    async def broadcast(self, peers):

        for peer in peers:

            async with aiohttp.ClientSession() as session:
                print(f'''posting information to http://{peer['name']}:{peer['port']}/info:''')
                pprint.pprint(self.identifiers)
                try:
                    await session.post(f'''http://{peer['name']}:{peer['port']}/info''', json=self.identifiers)
                except:
                    pass


    # ADD operation
    async def add_handler(self, request):
        identifier = request.match_info['identifier']
        print(f'receiving new file from client with identifier of {identifier}')

        # handle saving posted data
        body = await request.read()
        with open(f'{self.PIN_DIR}/{identifier}', 'wb') as file:
            file.write(body)

        # add to identifiers dict
        self.identifiers[identifier] = 'True'

        return web.Response()

    # INFO operation
    async def info_handler(self, request):
        print(f'receiving information from peer:')
        pprint.pprint(await request.json())
        return web.Response()

    # GET operation
    async def get_handler(self, request):
        identifier = request.match_info['identifier']
        print(f'providing client with file with identifier of {identifier}')
        return web.FileResponse(f'{self.PIN_DIR}/{identifier}')

    # server main loop
    async def serve(self):

        # set up app
        app = web.Application()
        
        app.add_routes([web.post('/info', self.info_handler),
                web.post('/add/{identifier}', self.add_handler),
                web.get('/get/{identifier}', self.get_handler)])

        # set up aiohttp server
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host=socket.getfqdn(), port=0, reuse_port=True)
        await site.start()

        # TODO: hacky... is there a way around this?
        self.port = site._server.sockets[0].getsockname()[1]
        self.host = socket.getfqdn()
        print(f'{self.host}:{self.port}')

        # run other tasks
        await asyncio.gather(self.update_nameserver(), self.retrieve_peers())

        # wait forever
        await asyncio.Event().wait()

if __name__ == '__main__':
    s = sPinServer(sys.argv[1])
    asyncio.run(s.serve())
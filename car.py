import asyncio
import websockets
import json
import ast
# file=sys.argv[1]
# # f = open("cars/"+file,'r')
# f = open(file,'r')
# data = json.load(f)        
# model = data["Model"]
# vendorName = data["Vendor"]
# reason = 'PowerUp'
# name = data["Id"]
# charge_req=data["Amount"]

async def on_connect(websocket, path):
    req = await websocket.recv()
    print(req)
    if req[0]=='c':
        f = open("cars/"+req,'r')
        data = json.load(f)  
        await websocket.send(str(data)) 
    else:
        import fcompact as fc
        challenge=ast.literal_eval(req)
        resp=fc.compact(challenge)
        await websocket.send(str(resp))





start_server = websockets.serve(on_connect, "localhost", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
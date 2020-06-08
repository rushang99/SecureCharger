import asyncio
import websockets
import pathlib
import ssl
from datetime import datetime
from ocpp.v20 import call
from ocpp.v20 import ChargePoint as cp
import sys
import pem
import subprocess
import time
import json
import ast


auth_flag=False
resp=[]
puff_auth=False
balance=0
message_id = 0
prev_msg_done = True

file=sys.argv[1]
response_done=False
authorization_done=False
f = open("cars/"+file,'r')
data = json.load(f)  
model = data["Model"]
vendorName = data["Vendor"]
reason = 'PowerUp'      
name = data["Id"]
charge_req=data["Amount"]

class ChargePoint(cp):


    async def send_boot_notification(self,model,vendorName,reason):
        global prev_msg_done

            
        request = call.BootNotificationPayload(
                charging_station={
                    'model': model,
                    'vendorName': vendorName
                },
                reason=reason
        )

        response = await self.call(request)
    
        
        if response.status == 'Accepted':
            prev_msg_done = True
            # print("Connected to central system.")
            # print("Response-- "+str(response))

        


    async def send_authorize(self,idToken,typee):
        global prev_msg_done
        request = call.AuthorizePayload(
                id_token={
                    'idToken': idToken,
                    'type': typee
                },
                # _15118_certificate_hash_data=None,
                # evse_id=None
        )
        response = await self.call(request)
        global auth_flag
        global balance
        if response.id_token_info['status'] == 'Accepted':
            auth_flag = True
            balance=response.evse_id[0]
            prev_msg_done = True
            # print(idToken+"-->Authorization Sucessful")

        elif response.id_token_info['status'] == 'Invalid':
            auth_flag=False
            balance=0
            # print("Invalid Name/Id. Please try again!")

        elif response.id_token_info['status'] == 'NotAtThisLocation':
            auth_flag=False
            balance=0
            # print("The user is already Authorized elsewhere. Please wait and try again later!!!")  


    async def send_transaction_event(self,eventType,triggerReason,seqNo,id):
    
        global prev_msg_done
        global authorization_done
        while(True):
            if authorization_done:
                break
            else:
                await asyncio.sleep(0)
        request = call.TransactionEventPayload(
                event_type=eventType,
                timestamp=datetime.utcnow().isoformat(),
                trigger_reason=triggerReason,
                seq_no=seqNo,
                transaction_data={'id': id}
        )
        prev_msg_done = True
        response = await self.call(request)
        # if response.charging_priority==-1:
            # print("Sufficient balance not available")
            # sys.exit(0)
        # elif response.charging_priority==9:
            # print("Transaction Started worth amount-- "+str(response.total_cost))
        # elif response.charging_priority==0:
            # print("Cannot start transaction")
        # elif response.charging_priority==-9:
        if response.charging_priority==-9:
            print("Charging finished worth-- "+str(response.total_cost))
            # await self._connection.close()
            


    async def send_data_transfer(self,info,id):
        global resp
        global response_done
        if info=="Request Challenge":
            
            request = call.DataTransferPayload(
                data=info,
                vendor_id=id
            )
            response = await self.call(request)
            
        else:
            
            while(True):
                if response_done:
                    break
                else:
                    await asyncio.sleep(0)
            
            response_done=False
            
            request = call.DataTransferPayload(
                data=resp,
                vendor_id=id
            )  
            response = await self.call(request)         


        
        global puff_auth
        global authorization_done
        
        if(response.status=='Rejected' and response.data!="Failed"):
            challenge=response.data
            # print("Challenge recieved-- "+ str(challenge))
            
            # import fcompact as fc           
            # start_time = time.time()
            # # uri = "ws://localhost:8765"
            # # async with websockets.connect(uri) as websocket:
            # #     send = str(challenge)

            # #     await websocket.send(send)
            # #     # print(f"> {name}")

            # #     rec = await websocket.recv()
                 
            # # resp=ast.literal_eval(rec)
            # # time_elapsed=(time.time() - start_time)
            # # resp.append(time_elapsed)

            # # print(resp) 

            # resp=fc.compact(challenge)   
            # time_elapsed=(time.time() - start_time)
            # resp.append(time_elapsed)              
            # # print(str(response)+" "+str(time_elapsed))

            # # print("Response Recorded")

            output=subprocess.Popen( ['python3', 'test_compact.py', str(challenge)], stdout=subprocess.PIPE ).communicate()[0]
            arr=str(output).split("\\n")
            resp=arr[1].split()[:4]

            for i in range(4):
                resp[i]=int(resp[i])

            time=float(arr[2])
            resp.append(time)
            
            response_done=True

        elif response.status=="Accepted" and response.data=="Done":            
            puff_auth=True
            prev_msg_done = True
            authorization_done=True
            # print("PUF Authorization Successful")

        elif response.status=="Rejected" and response.data=="Failed":            
            puff_auth=False
            authorization_done=False
            # print("PUF Authorization Unsuccessful")

        # else:
            # print(response.data)





ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE
ssl_context.load_verify_locations("cert.pem")

async def main(): 
    global name   
    try:      
        async with websockets.connect(
            'wss://localhost:9000/CP_1',
                subprotocols=['ocpp2.0'],
                ssl=ssl_context,
                ping_interval = 7
        ) as ws:        
            cp = ChargePoint('CP_1', ws)
            global resp
            global message_id
            global prev_msg_done
            global model
            global vendorName
            global charge_req

            uri = "ws://localhost:8765"
            async with websockets.connect(uri) as websocket:
                send = file

                await websocket.send(send)
                # print(f"> {name}")

                rec = await websocket.recv()
                data=eval(rec)
                # print(f"< {rec}")  
                model = data["Model"]
                vendorName = data["Vendor"]
                reason = 'PowerUp'      
                name = data["Id"]
                charge_req=data["Amount"]
            
            await asyncio.gather(cp.start(),cp.send_boot_notification(model,vendorName,'PowerUp'),cp.send_authorize(name, 'Central'),cp.send_data_transfer("Request Challenge","Challenge"),cp.send_data_transfer(resp,"Challenge Sent"),cp.send_transaction_event('Started', 'Authorized', int(charge_req), 'Hello World'),cp.send_transaction_event('Ended', 'EVDeparted', 1234, 'Hello World'), cp._connection.close())
            # await asyncio.gather(cp.start(),cp.send_boot_notification(model,vendorName,'PowerUp'))
    except Exception:
        print("Exception")


if __name__ == '__main__':         
    asyncio.run(main())

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



auth_flag=False
resp=[]
puff_auth=False
balance=0
message_id = 0
prev_msg_done = True
file=sys.argv[1]
f = open("cars/"+file,'r')
data = json.load(f)        
model = data["Model"]
vendorName = data["Vendor"]
reason = 'PowerUp'
name = data["Id"]
charge_req=data["Amount"]
response_done=False
authorization_done=False


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
            print("Connected to central system.")
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
            print(idToken+"-->Authorization Sucessful")
            # print(response)
        elif response.id_token_info['status'] == 'Invalid':
            auth_flag=False
            balance=0
            print("Invalid Name/Id. Please try again!")

        elif response.id_token_info['status'] == 'NotAtThisLocation':
            auth_flag=False
            balance=0
            print("The user is already Authorized elsewhere. Please wait and try again later!!!")  

    async def send_cancel_reservation(self, reservId):
        request = call.CancelReservationPayload(
                reservation_id= reservId
        )
        response = await self.call(request)
        # if response.status == 'Accepted':
        #     # print("Reservation Cancelled")
        #     # print(response) 

    async def send_set_variables(self):
        request = call.SetVariablesPayload(
                set_variable_data=[{'attributeValue': 'str', 'component': {'name': 'comp'}, 'variable': {'name': 'var'}}]
        )
        response = await self.call(request)

        # if response.set_variable_result[0]['attribute_status'] == 'Accepted':
        #     # print("Variables Set")
        #     # print(response) 
        
    async def send_get_variables(self):
        request = call.GetVariablesPayload(
                get_variable_data=[{'component': {'name': 'comp'}, 'variable': {'name': 'var'}}]
        )
        response = await self.call(request)

        # if response.get_variable_result[0]['attribute_status'] == 'Accepted':
        #     # print("Variables Recieved")
        #     # print(response) 

    async def send_get_report(self, reportId):
        request = call.GetReportPayload(
                request_id = reportId
        )
        response = await self.call(request)

        # if response.status == 'Accepted':
        #     # print("Report Recieved")
        #     # print(response)

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
        if response.charging_priority==-1:
            # print("Sufficient balance not available")
            sys.exit(0)
        # elif response.charging_priority==9:
        #     # print("Transaction Started worth amount-- "+str(response.total_cost))
        # elif response.charging_priority==0:
        #     print("Cannot start transaction")
        elif response.charging_priority==-9:
            # print("Charging finished worth-- "+str(response.total_cost))
            print("Done")
            

    async def send_reset(self,typee):
        request = call.ResetPayload(
                type=typee
        )
        response = await self.call(request)

        # if response.status=='Accepted':
        #     # print('Resetting')
        #     # print(response)

    async def send_change_availability(self,id,status):
        request = call.ChangeAvailabilityPayload(
                operational_status=status,
                evse_id=id
        )
        response = await self.call(request)

        # if response.status=='Accepted':
        #     # print('Changing availability')
        #     # print(response)

    async def send_status_notification(self,status,evse_id,connector_id):
        request = call.StatusNotificationPayload(
                timestamp=datetime.utcnow().isoformat(),
                connector_status=status,
                evse_id=evse_id,
                connector_id=connector_id
        )
        response = await self.call(request)

        # print(response)

    async def send_notify_event(self,tbc,seqNo,trigger,actualValue,cleared,eventNotificationType,componentName,variableName):
        request = call.NotifyEventPayload(
                generated_at=datetime.utcnow().isoformat(),
                tbc=tbc,
                seq_no=seqNo,
                event_data=[{'eventId': 1234, 'timestamp': 'datetime', 'trigger': trigger, 'actualValue': actualValue,'cleared': cleared, 'eventNotificationType': eventNotificationType, 'component': {'name': componentName}, 'variable': {'name': variableName}}]
        )
        response = await self.call(request)

        # print(response)

    async def send_data_transfer(self,info,id):
        global resp
        if info=="Request Challenge":
            
            request = call.DataTransferPayload(
                data=info,
                vendor_id=id
            )
            response = await self.call(request)
            
        else:
            global response_done
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
            print("Challenge recieved-- "+ str(challenge))
            
            import fcompact as fc
            
            global prev_msg_done
            start_time = time.time()
            # print(challenge)
            resp=fc.compact(challenge)
            time_elapsed=(time.time() - start_time)
            resp.append(time_elapsed)
            # print(resp)                     
            # print(str(response)+" "+str(time_elapsed))
            prev_msg_done = True
            # print("Response Recorded")
            
            response_done=True

        elif response.status=="Accepted" and response.data=="Done":            
            puff_auth=True
            prev_msg_done = True
            authorization_done=True
            print("PUF Authorization Successful")

        elif response.status=="Rejected" and response.data=="Failed":            
            puff_auth=False
            authorization_done=False
            print("PUF Authorization Unsuccessful")

        # else:
        #     # print(response.data)

    


    async def send_clear_cache(self):
        request = call.ClearCachePayload(
            
        )
        response = await self.call(request)

        print(response)

    async def send_clear_charging_profile(self,evseid):
        request = call.ClearChargingProfilePayload(
            evse_id=evseid
        )
        response = await self.call(request)

        print(response)

    async def send_clear_display_message(self,id):
        request = call.ClearDisplayMessagePayload(
            id=id
        )
        response = await self.call(request)

        print(response)

    async def send_clear_variable_monitoring(self,id):
        request = call.ClearVariableMonitoringPayload(
            id=id
        )
        response = await self.call(request)

        print(response)

    async def send_cost_updated(self,totalCost,transactionId):
        request = call.CostUpdatedPayload(
            total_cost=totalCost,
            transaction_id=transactionId
        )
        response = await self.call(request)

        print(response)

    async def send_firmware_status_notification(self,status,requestid):
        request = call.FirmwareStatusNotificationPayload(
            request_id=requestid,
            status=status
        )
        response = await self.call(request)

        print(response)

    async def send_get_charging_profiles(self,chargingProfile):
        request = call.GetChargingProfilesPayload(
            charging_profile=chargingProfile
        )
        response = await self.call(request)

        print(response)

    async def send_get_composite_schedule(self,evseid,duration):
        request = call.GetCompositeSchedulePayload(
            evse_id=evseid,
            duration=duration
        )
        response = await self.call(request)

        print(response)

    async def send_get_display_messages(self,requestid):
        request = call.GetDisplayMessagesPayload(
            request_id=requestid
        )
        response = await self.call(request)

        print(response)

    async def send_get_local_list_version(self):
        request = call.GetLocalListVersionPayload(
            
        )
        response = await self.call(request)
        print(response)

    async def send_get_monitoring_report(self,requestid):
        request = call.GetMonitoringReportPayload(
            request_id=requestid
        )
        response = await self.call(request)
        print(response)

    async def send_get_transaction_status(self,transactionId):
        request = call.GetTransactionStatusPayload(
            transaction_id=transactionId
        )
        response = await self.call(request)
        print(response)



ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE
ssl_context.load_verify_locations("cert.pem")


async def main(): 
    global name         
    async with websockets.connect(
        'wss://localhost:9000/'+name,
            subprotocols=['ocpp2.0'],
            ssl=ssl_context,
            ping_interval = 7
    ) as ws:        
        cp = ChargePoint(name, ws)
        global resp
        global message_id
        global prev_msg_done
        global model
        global vendorName
        global charge_req
        

        await asyncio.gather(cp.start(),cp.send_boot_notification(model,vendorName,'PowerUp'),cp.send_authorize(name, 'Central'),cp.send_data_transfer("Request Challenge","Challenge"),cp.send_data_transfer(resp,"Challenge Sent"),cp.send_transaction_event('Started', 'Authorized', int(charge_req), 'Hello World'),cp.send_transaction_event('Ended', 'EVDeparted', 1234, 'Hello World'))
        # ws.close()
        

if __name__ == '__main__':         
    asyncio.run(main())

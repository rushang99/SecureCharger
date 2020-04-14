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

auth_flag=False
resp=[]
puff_auth=False
balance=0


class ChargePoint(cp):

    async def send_boot_notification(self,model,vendorName,reason):
        request = call.BootNotificationPayload(
                charging_station={
                    'model': model,
                    'vendorName': vendorName
                },
                reason=reason
        )
        response = await self.call(request)
        
        if response.status == 'Accepted':
            print("Connected to central system.")
            print("Response-- "+str(response))


    async def send_authorize(self,idToken,typee):
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
            print("Authorization Sucessful")
            # print(response)
        else:
            auth_flag=False
            balance=0
            print("Invalid Name/Id. Please try again!")

    async def send_cancel_reservation(self, reservId):
        request = call.CancelReservationPayload(
                reservation_id= reservId
        )
        response = await self.call(request)
        if response.status == 'Accepted':
            print("Reservation Cancelled")
            print(response) 

    async def send_set_variables(self):
        request = call.SetVariablesPayload(
                set_variable_data=[{'attributeValue': 'str', 'component': {'name': 'comp'}, 'variable': {'name': 'var'}}]
        )
        response = await self.call(request)

        if response.set_variable_result[0]['attribute_status'] == 'Accepted':
            print("Variables Set")
            print(response) 
        
    async def send_get_variables(self):
        request = call.GetVariablesPayload(
                get_variable_data=[{'component': {'name': 'comp'}, 'variable': {'name': 'var'}}]
        )
        response = await self.call(request)

        if response.get_variable_result[0]['attribute_status'] == 'Accepted':
            print("Variables Recieved")
            print(response) 

    async def send_get_report(self, reportId):
        request = call.GetReportPayload(
                request_id = reportId
        )
        response = await self.call(request)

        if response.status == 'Accepted':
            print("Report Recieved")
            print(response) 

    async def send_transaction_event(self,eventType,triggerReason,seqNo,id):
        request = call.TransactionEventPayload(
                event_type=eventType,
                timestamp=datetime.utcnow().isoformat(),
                trigger_reason=triggerReason,
                seq_no=seqNo,
                transaction_data={'id': id}
        )
        response = await self.call(request)
        print(response)
        print(response.total_cost)

    async def send_reset(self,typee):
        request = call.ResetPayload(
                type=typee
        )
        response = await self.call(request)

        if response.status=='Accepted':
            print('Resetting')
            print(response)

    async def send_change_availability(self,id,status):
        request = call.ChangeAvailabilityPayload(
                operational_status=status,
                evse_id=id
        )
        response = await self.call(request)

        if response.status=='Accepted':
            print('Changing availability')
            print(response)

    async def send_status_notification(self,status,evse_id,connector_id):
        request = call.StatusNotificationPayload(
                timestamp=datetime.utcnow().isoformat(),
                connector_status=status,
                evse_id=evse_id,
                connector_id=connector_id
        )
        response = await self.call(request)

        print(response)

    async def send_notify_event(self,tbc,seqNo,trigger,actualValue,cleared,eventNotificationType,componentName,variableName):
        request = call.NotifyEventPayload(
                generated_at=datetime.utcnow().isoformat(),
                tbc=tbc,
                seq_no=seqNo,
                event_data=[{'eventId': 1234, 'timestamp': 'datetime', 'trigger': trigger, 'actualValue': actualValue,'cleared': cleared, 'eventNotificationType': eventNotificationType, 'component': {'name': componentName}, 'variable': {'name': variableName}}]
        )
        response = await self.call(request)

        print(response)

<<<<<<< HEAD
    async def send_data_transfer(self,info,id):
        request = call.DataTransferPayload(
            data=info,
            vendor_id=id
        )

        response = await self.call(request)
        global puff_auth
        if(response.status=='Rejected' and response.data!="Failed"):
            challenge=response.data
            print("Challenge recieved-- "+ str(challenge))
            
            import fcompact as fc
            global resp
            start_time = time.time()
            resp=fc.compact(challenge)
            time_elapsed=(time.time() - start_time)
            resp.append(time_elapsed)
            # print(str(response)+" "+str(time_elapsed))
            print("Response Recorded")

        elif response.status=="Accepted" and response.data=="Done":
            
            puff_auth=True
            print("PUF Authorization Successful")

        elif response.status=="Rejected" and response.data=="Failed":
            
            puff_auth=False
            print("PUF Authorization Unsuccessful")

        else:
            print(response.data)


    async def send_clear_cache(self):
        request = call.ClearCachePayload(
            
=======
    async def send_clear_cache(self):
        request = call.ClearCachePayload(
        	
>>>>>>> 9e696812c6fa8b5812cbcf6f216dbd352c659daf
        )
        response = await self.call(request)

        print(response)

    async def send_clear_charging_profile(self,evseid):
        request = call.ClearChargingProfilePayload(
<<<<<<< HEAD
            evse_id=evseid
=======
        	evse_id=evseid
>>>>>>> 9e696812c6fa8b5812cbcf6f216dbd352c659daf
        )
        response = await self.call(request)

        print(response)

    async def send_clear_display_message(self,id):
        request = call.ClearDisplayMessagePayload(
<<<<<<< HEAD
            id=id
=======
        	id=id
>>>>>>> 9e696812c6fa8b5812cbcf6f216dbd352c659daf
        )
        response = await self.call(request)

        print(response)

    async def send_clear_variable_monitoring(self,id):
        request = call.ClearVariableMonitoringPayload(
<<<<<<< HEAD
            id=id
=======
        	id=id
>>>>>>> 9e696812c6fa8b5812cbcf6f216dbd352c659daf
        )
        response = await self.call(request)

        print(response)

    async def send_cost_updated(self,totalCost,transactionId):
        request = call.CostUpdatedPayload(
<<<<<<< HEAD
            total_cost=totalCost,
            transaction_id=transactionId
=======
        	total_cost=totalCost,
        	transaction_id=transactionId
>>>>>>> 9e696812c6fa8b5812cbcf6f216dbd352c659daf
        )
        response = await self.call(request)

        print(response)

    async def send_firmware_status_notification(self,status,requestid):
        request = call.FirmwareStatusNotificationPayload(
<<<<<<< HEAD
            request_id=requestid,
            status=status
=======
        	request_id=requestid,
        	status=status
>>>>>>> 9e696812c6fa8b5812cbcf6f216dbd352c659daf
        )
        response = await self.call(request)

        print(response)

    async def send_get_charging_profiles(self,chargingProfile):
        request = call.GetChargingProfilesPayload(
<<<<<<< HEAD
            charging_profile=chargingProfile
=======
        	charging_profile=chargingProfile
>>>>>>> 9e696812c6fa8b5812cbcf6f216dbd352c659daf
        )
        response = await self.call(request)

        print(response)

    async def send_get_composite_schedule(self,evseid,duration):
        request = call.GetCompositeSchedulePayload(
<<<<<<< HEAD
            evse_id=evseid,
            duration=duration
=======
        	evse_id=evseid,
        	duration=duration
>>>>>>> 9e696812c6fa8b5812cbcf6f216dbd352c659daf
        )
        response = await self.call(request)

        print(response)

    async def send_get_display_messages(self,requestid):
        request = call.GetDisplayMessagesPayload(
<<<<<<< HEAD
            request_id=requestid
=======
        	request_id=requestid
>>>>>>> 9e696812c6fa8b5812cbcf6f216dbd352c659daf
        )
        response = await self.call(request)

        print(response)

    async def send_get_local_list_version(self):
        request = call.GetLocalListVersionPayload(
<<<<<<< HEAD
            
=======
        	
>>>>>>> 9e696812c6fa8b5812cbcf6f216dbd352c659daf
        )
        response = await self.call(request)

        print(response)

    async def send_get_monitoring_report(self,requestid):
        request = call.GetMonitoringReportPayload(
<<<<<<< HEAD
            request_id=requestid
=======
        	request_id=requestid
>>>>>>> 9e696812c6fa8b5812cbcf6f216dbd352c659daf
        )
        response = await self.call(request)

        print(response)

    async def send_get_transaction_status(self,transactionId):
        request = call.GetTransactionStatusPayload(
<<<<<<< HEAD
            transaction_id=transactionId
=======
        	transaction_id=transactionId
>>>>>>> 9e696812c6fa8b5812cbcf6f216dbd352c659daf
        )
        response = await self.call(request)

        print(response)


ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE
ssl_context.load_verify_locations("cert.pem")





async def main():          
    async with websockets.connect(
        'wss://localhost:9000/CP_1',
         subprotocols=['ocpp2.0'],
         ssl=ssl_context,
         ping_interval = 7
    ) as ws:        
        cp = ChargePoint('CP_1', ws)
        print("")
        print("Please enter a message to send to the CSMS")
        message = str(input())
        if message == 'Boot Notification':
                print("Enter Model:")
                model  = str(input())
                print("Enter Vendor Name:")
                vendorName = str(input())
                print("Enter Reason:")
                reason = str(input())
                # asyncio.ensure_future(cp.start())
                # asyncio.ensure_future(cp.send_boot_notification(model,vendorName,reason))                
                await asyncio.gather(cp.start(), cp.send_boot_notification(model,vendorName,reason), asyncio.ensure_future(main()))                

        elif message == 'Notify Event':
                print
                await asyncio.gather(cp.start(), cp.send_notify_event(False,0,'Alerting','actualValue',True,'HardWiredNotification','comp','var'), asyncio.ensure_future(main()))

        elif message == "Get Report":
                print("Enter Report Id")
                reportId = int(input())
                print(reportId)
                await asyncio.gather(cp.start(), cp.send_get_report(reportId), asyncio.ensure_future(main()))
        elif message == "Authorize":
                print("Enter Name/Id")
                name = str(input())
                await asyncio.gather(cp.start(), cp.send_authorize(name, 'Central'), asyncio.ensure_future(main())) 
        elif message == "Transaction Start":
                global auth_flag
                global puff_auth
                if(auth_flag and puff_auth):
                    global balance
                    print("Enter Charging Amount")
                    charge_req=str(input())
                    if(int(charge_req) <= balance):
                        await asyncio.gather(cp.start(),cp.send_transaction_event('Started', 'Authorized', int(charge_req), 'Hello World'), asyncio.ensure_future(main())) 
                    else:
                        print("Sufficient Balance not available. Please recharge")
                        await asyncio.ensure_future(main())
                else:
                    print("Transaction is not authorized")
                    await asyncio.ensure_future(main())
        elif message == "Transaction End":
                await asyncio.gather(cp.start(),cp.send_transaction_event('Ended', 'EVDeparted', 1234, 'Hello World'), asyncio.ensure_future(main())) 
        elif message == "Data Transfer":
                await asyncio.gather(cp.start(),cp.send_data_transfer("1234","Normal"), asyncio.ensure_future(main())) 
        elif message == "Request Challenge":
                await asyncio.gather(cp.start(),cp.send_data_transfer("Request Challenge","Challenge"), asyncio.ensure_future(main())) 
        elif message == "Request Validation":
                global resp
                await asyncio.gather(cp.start(),cp.send_data_transfer(resp,"Challenge Sent"), asyncio.ensure_future(main())) 
        else:
                print("Please enter a valid message")
                await asyncio.ensure_future(main())
                
        
        

if __name__ == '__main__':           
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
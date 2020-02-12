import asyncio
import websockets
import pathlib
import ssl
from datetime import datetime
from ocpp.v20 import call
from ocpp.v20 import ChargePoint as cp
import sys

auth_flag = False

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
            print(response)


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
        if response.id_token_info['status'] == 'Accepted':
            auth_flag = True
            print("Authorization Sucessful")
            print(response)
        else:
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

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE
ssl_context.load_verify_locations("cert.pem")





async def main():
    
    async with websockets.connect(
        'wss://192.168.43.29:9000/CP_1',
         subprotocols=['ocpp2.0'],
         ssl=ssl_context
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
        elif message == "Transaction":
                await asyncio.gather(cp.start(),cp.send_transaction_event('Started', 'Authorized', 1234, 'Hello World'), asyncio.ensure_future(main())) 
        else:
                print("Please enter a valid message")

if __name__ == '__main__':
        asyncio.run(main())


    

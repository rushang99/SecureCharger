import asyncio
import websockets
from datetime import datetime
from ocpp.v20 import call
from ocpp.v20 import ChargePoint as cp


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
            print("Authorization Sucessful")
            print(response)

    async def send_cancel_reservation(self):
        request = call.CancelReservationPayload(
                reservation_id=1234567
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

    async def send_get_report(self):
        request = call.GetReportPayload(
                request_id=123456789
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

        print(response.total_cost)

async def main():
    async with websockets.connect(
        'ws://192.168.43.217:9000/CP_1',
         subprotocols=['ocpp2.0']
    ) as ws:

        cp = ChargePoint('CP_1', ws)

        await asyncio.gather(cp.start(), cp.send_boot_notification('ModelName','VendorName','PowerUp'),cp.send_transaction_event('Ended','Authorized',12,'1345'))
        
        


if __name__ == '__main__':
    asyncio.run(main())

import asyncio
import websockets

from ocpp.v20 import call
from ocpp.v20 import ChargePoint as cp


class ChargePoint(cp):

    async def send_boot_notification(self):
        request = call.BootNotificationPayload(
                charging_station={
                    'model': 'Wallbox XYZ',
                    'vendorName': 'anewone'
                },
                reason="PowerUp"
        )
        response = await self.call(request)
        
        if response.status == 'Accepted':
            print("Connected to central system.")
            print(response)


    async def send_authorize(self):
        request = call.AuthorizePayload(
                idToken={
                    'idToken': '1234567890',
                    'type': 'Central'
                },
                # _15118_certificate_hash_data=None,
                # evse_id=None
        )
        response = await self.call(request)
        if response.id_token_info['status'] == 'Accepted':
            print("Authorization Sucessful")
            print(response)

async def main():
    async with websockets.connect(
        'ws://192.168.43.217:9000/CP_1',
         subprotocols=['ocpp2.0']
    ) as ws:

        cp = ChargePoint('CP_1', ws)

        await asyncio.gather(cp.start(), cp.send_boot_notification())
        await asyncio.gather(cp.start(), cp.send_authorize())
        


if __name__ == '__main__':
    asyncio.run(main())

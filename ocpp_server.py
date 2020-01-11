import asyncio
import websockets
from datetime import datetime

from ocpp.routing import on
from ocpp.v20 import ChargePoint as cp
from ocpp.v20 import call_result

class ChargePoint(cp):
    @on('BootNotification')
    def on_boot_notitication(self, charging_station, reason, **kwargs):
        return call_result.BootNotificationPayload(
            current_time = datetime.utcnow().isoformat(),
            interval = 10,
            status ='Accepted'
        )

    @on('Authorize')
    def on_authorize(self, id_token, evse_id, **kwargs):
        # can add certificate _15118_certificate_hash_data
        return call_result.AuthorizePayload(
            id_token_info = {
                'status' : 'Accepted',
                # 'cacheExpiryDateTime'
                # 'ChargePriority'
                # 'language1'        
            }
            # certificate_status =
            # evse_id =
        )

async def on_connect(websocket, path):
    """ For every new charge point that connects, create a ChargePoint instance
    and start listening for messages.

    """
    charge_point_id = path.strip('/')
    cp = ChargePoint(charge_point_id, websocket)

    await cp.start()

async def main():
    server = await websockets.serve(
        on_connect,
        '0.0.0.0',
        9000,
        subprotocols=['ocpp2.0']
    )

    await server.wait_closed()

if __name__ == '__main__':
    asyncio.run(main())
import asyncio
import websockets
from datetime import datetime

from ocpp.routing import on
from ocpp.v20 import ChargePoint as cp
from ocpp.v20 import call_result
import pathlib
import ssl

class ChargePoint(cp):
    @on('BootNotification')
    def on_boot_notitication(self, charging_station, reason, **kwargs):
        print(charging_station['model'] + ' from ' + charging_station['vendor_name'] + ' has booted.')
        return call_result.BootNotificationPayload(
            current_time = datetime.utcnow().isoformat(),
            interval = 10,
            status ='Accepted'
        )

    @on('Authorize')
    def on_authorize(self, id_token, **kwargs):
        print(id_token + 'authorized successfully.')
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

    @on('CancelReservation')
    def on_cancel_reservation(self, reservation_id):
        print('Reservation of '+ reservation_id + ' cancelled')
        return call_result.CancelReservationPayload(
            status = 'Accepted'
        )

    @on('SetVariables')
    def set_variables(self, set_variable_data):
        print('SetVariables')
        return call_result.SetVariablesPayload(
            set_variable_result = [{
                'attributeStatus':'Accepted',
                'component' : {'name': 'ComponentType'},
                'variable': {'name': 'VariableType'}
            }]
        )

    @on('GetVariables')
    def get_variables(self, get_variable_data):
        print('GetVariables')
        return call_result.GetVariablesPayload(
            get_variable_result = [
                {
                    'attributeStatus':'Accepted',
                    'component' : {'name': 'ComponentType'}, 
                    'variable': {'name': 'VariableType'}
                }
            ]
        )

    @on('GetReport')
    def get_report(self, request_id, **kwargs):
        print('GetReport')
        return call_result.GetReportPayload(
            status  = 'Accepted'
        )

    @on('TransactionEvent')
    def transaction_event(self, event_type, timestamp, trigger_reason, seq_no, transaction_data, **kwargs):
        print('TransactionEvent')
        return call_result.TransactionEventPayload(
            total_cost = 1500.00,
            charging_priority = 2
        ) 

    @on('Reset')
    def reset(self, type, **kwargs):
        print(type + ' reset requested')
        return call_result.ResetPayload(
            status = 'Accepted'
        )

    @on('ChangeAvailability')
    def change_availability(self, operational_status, **kwargs):
        print('Availability changed to ' + operational_status)
        return call_result.ChangeAvailabilityPayload(
            status = 'Accepted'
        )

    @on('StatusNotification')
    def status_notification(self, timestamp, connector_status, evse_id, connector_id):
        print(timestamp + ' Connector of '+ str(connector_id)+ ' is ' + connector_status)
        return call_result.StatusNotificationPayload(

        )

    @on('NotifyEvent')
    def notify_event(self, generated_at, tbc, seq_no, event_data, **kwargs):
        print('An event occured at '+ generated_at)
        return call_result.NotifyEventPayload(

        )



async def on_connect(websocket, path):
    """ For every new charge point that connects, create a ChargePoint instance
    and start listening for messages.

    """
    charge_point_id = path.strip('/')
    cp = ChargePoint(charge_point_id, websocket)
    await cp.start()


ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain("cert.pem")
async def main():
    server = await websockets.serve(
        on_connect,
        '0.0.0.0',
        9000,
        subprotocols=['ocpp2.0'],
        ssl=ssl_context
        
    )

    await server.wait_closed()

if __name__ == '__main__':
    asyncio.run(main())
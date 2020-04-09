import asyncio
import websockets
from datetime import datetime

from ocpp.routing import on
from ocpp.v20 import ChargePoint as cp
from ocpp.v20 import call_result
import pathlib
import ssl
import pyrebase

config = {
    "apiKey": "AIzaSyAGas29t240FwqdvXjdwzz4kITTN2Ix1ro",
    "authDomain": "charger-1eb48.firebaseapp.com",
    "databaseURL": "https://charger-1eb48.firebaseio.com",
    "projectId": "charger-1eb48",
    "storageBucket": "charger-1eb48.appspot.com",
    "messagingSenderId": "430093083458",
    "serviceAccount": "/home/rushang99/Downloads/SecureCharger/secure.json"
}


firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
email = "guptaraghav1999@gmail.com"
password = "12345678"
user = auth.sign_in_with_email_and_password(email,password)
db = firebase.database()

cost='0'


class ChargePoint(cp):

    @on('BootNotification')
    def on_boot_notitication(self, charging_station, reason, **kwargs):
        print(charging_station['model'] + ' from ' + charging_station['vendor_name'] + ' has booted.')
        return call_result.BootNotificationPayload(
            current_time = datetime.utcnow().isoformat(),
            interval = 10,
            status = 'Accepted'
        )

    @on('Authorize')
    def on_authorize(self, id_token, **kwargs):
        name=id_token['id_token']
        flag=False
        all_users = db.child("Users").get()
        global cost
        for user in all_users.each():
            # print(user.key())
            # print(user.val()['name'])
            if user.val()['username']==name:
                flag=True
                break
        if flag:
            print(name + ' authorized successfully.')
            # can add certificate _15118_certificate_hash_data

            cost=user.val()['chargingCost']
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

        else:
            print(name + ' authorized unsuccessfully.')
            # can add certificate _15118_certificate_hash_data
            
            cost='0'
            return call_result.AuthorizePayload(
                id_token_info = {
                    'status' : 'Invalid',
                    # 'cacheExpiryDateTime'
                    # 'ChargePriority'
                    # 'language1'        
                }
                # certificate_status =
                # evse_id =
            )            

    @on('ClearCache')
    def clear_cache(self):
        print('Clear Cache request set')
        return call_result.ClearCachePayload(
            status = 'Accepted'
        )

    @on('ClearChargingProfile')
    def clear_charging_profile(self, evse_id, **kwargs):
        return call_result.ClearChargingProfilePayload(
            status = 'Accepted'
        )

    @on('ClearDispplayMessage')
    def clear_display_message(self, id):
        return call_result.ClearDisplayMessagePayload(
            status = 'Accepted'
        )

    @on('ClearVariableMonitoring')
    def clear_variable_monitor(self, id):
        return call_result.ClearVariableMonitoringPayload(
            id = id,
            status = 'Accepted'
        )

    @on('CostUpdated')
    def cost_updated(self, total_cost, transaction_id):
        return call_result.CostUpdatedPayload(

        )

    @on('FirmwareStatusNotification')
    def firmware_status_notification(self, status, request_id):
        return call_result.FirmwareStatusNotificationPayload(

        )

    @on('GetChargingProfiles')
    def get_charging_profiles(self, request_id, evse_id, clear_charging_profile):
        return call_result.GetChargingProfilesPayload(
            status = 'Accepted'
        )

    @on('GetCopmpositeSchedule')
    def get_composite_schedule(self, duration, charging_rate_unit, evse_id):
        return call_result.GetCompositeSchedulePayload(
            status = 'Accepted',
            schedule = None
        )

    @on('GetDisplayMessages')
    def get_display_messages(self, id, request_id, priority, state):
        return call_result.GetDisplayMessagesPayload(
            status = 'Accepted'
        )

    @on('GetLocalListVersion')
    def get_local_list_version(self):
        return call_result.GetLocalListVersionPayload(
            version_number = 123
        )

    @on('GetMonitoringReport')
    def get_monitoring_report(self, request_id):
        return call_result.GetMonitoringReportPayload(
            status = 'Accepted'
        )

    @on('GetTransactionStatus')
    def get_transaction_status(self, transaction_id):
        return call_result.GetTransactionStatusPayload(
            messages_in_queue = True
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
        global cost
        return call_result.TransactionEventPayload(
            total_cost = int(cost),
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
        ssl=ssl_context,
        ping_timeout=100000000      
    )

    await server.wait_closed()

if __name__ == '__main__':
    asyncio.run(main())

import asyncio
import websockets
from datetime import datetime

from ocpp.routing import on
from ocpp.v20 import ChargePoint as cp
from ocpp.v20 import call_result
import pathlib
import ssl
import pyrebase
import subprocess
import pem
import random
import sys
import time

config = {
    "apiKey": "AIzaSyAGas29t240FwqdvXjdwzz4kITTN2Ix1ro",
    "authDomain": "charger-1eb48.firebaseapp.com",
    "databaseURL": "https://charger-1eb48.firebaseio.com",
    "projectId": "charger-1eb48",
    "storageBucket": "charger-1eb48.appspot.com",
    "messagingSenderId": "430093083458",
    # "serviceAccount": "/home/raghav/SecureCharger/secure.json"
    "serviceAccount": "/home/rushang99/Downloads/SecureCharger/secure.json"
}


firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
email = "guptaraghav1999@gmail.com"
password = "12345678"
user = auth.sign_in_with_email_and_password(email,password)
db = firebase.database()

count=0

class ChargePoint(cp):
    cost='0'
    userName=''
    modelName=''
    challenge=[0,0,0,0,0,0,0,0,0,0,0,0]
    db_auth=False
    puf_auth=False
    start_transaction=False
    charge_requested = 0
    start_time = 0
    end_time = 0

    @on('BootNotification')
    def on_boot_notitication(self, charging_station, reason, **kwargs):
        self.start_time = time.time()
        print(charging_station['model'] + ' from ' + charging_station['vendor_name'] + ' has booted.')
        self.modelName=charging_station['model']
        return call_result.BootNotificationPayload(
            current_time = datetime.utcnow().isoformat(),
            interval = 10,
            status = 'Accepted'
        )

    @on('Authorize')
    def on_authorize(self, id_token, **kwargs):
        name=id_token['id_token']
        flag=False
        db = firebase.database()
        all_users = db.child("Users").get()

        for user in all_users.each():
            if user.key()==name:
                flag=True
                break

        if flag:            
            
            lockAcquired = user.val()['userLock']
            # print(lockAcquired)
            if lockAcquired:
                print("The user is already Authorized elsewhere. Please wait and try again later!!!")  
                return call_result.AuthorizePayload(
                    id_token_info = {
                        'status' : 'NotAtThisLocation',
                        # 'cacheExpiryDateTime'
                        # 'ChargePriority'
                        # 'language1'        
                    },
                    # certificate_status = 
                    evse_id = [int(self.cost)]
                )          
            else:     
                # Get PUF model from database (To be done later)       
                self.cost=user.val()['chargingCost']
                self.db_auth=True
                print(name + ' authorized successfully.')
                print("Available balance of "+name + " " + str(self.cost))
                db.child("Users").child(name).update({"userLock" : True})
                self.userName=name
                print(self.userName)
                return call_result.AuthorizePayload(
                    id_token_info = {
                        'status' : 'Accepted',
                        # 'cacheExpiryDateTime'
                        # 'ChargePriority'
                        # 'language1'        
                    },
                    # certificate_status = 
                    evse_id = [int(self.cost)]
                )

        else:
            print(name + ' not found in database.')
            self.db_auth=False
            self.cost='0'
            self.userName=''
            self.modelName=''
            self.puf_auth=False
            self.start_transaction=False
            self.charge_requested=0
            self.challenge=[0,0,0,0,0,0,0,0,0,0,0,0]
            return call_result.AuthorizePayload(
                id_token_info = {
                    'status' : 'Invalid',
                    # 'cacheExpiryDateTime'
                    # 'ChargePriority'
                    # 'language1'        
                },
                # certificate_status =
                evse_id = [0]
            )            

    @on('DataTransfer')
    def data_transfer(self,data,vendor_id,**kwargs):

        if(self.db_auth):

            if(str(data)=="Request Challenge"):
                #Generate Challenge
                
                n=random.randrange(0,4096,1)
                bn=str(bin(n).replace("0b",""))
                for i in range(len(bn)):
                    self.challenge[12-len(bn)+i]=(ord(bn[i])-ord('0'))
                print("Challenge Generated-- " + str(self.challenge))
                return call_result.DataTransferPayload(
                    status = 'Rejected',
                    data=self.challenge
                )
            elif(str(vendor_id)=="Challenge Sent"):
                
                #Request model from database and validate user
                import fexpand as fe
                start_time = time.time()
                response_expand=fe.expand(self.challenge)
                time_expand=(time.time() - start_time)
                response_compact=data[:4]
                time_compact=data[4]

                if (time_compact < time_expand) and time_compact<1e-4  and time_expand > 1e-5 and response_compact==response_expand:
                    # print(time_expand - time_compact)
                    print("time_expand--"+str(time_expand))
                    print("time_compact--"+str(time_compact))
                    print("PUF authorization successful")
                    self.puf_auth=True
                    return call_result.DataTransferPayload(
                        status = 'Accepted',
                        data="Done"
                    )
                else:
                    # print(time_expand - time_compact)
                    print("time_expand--"+str(time_expand))
                    print("time_compact--"+str(time_compact))
                    print("PUF authorization unsuccessful")
                    db.child("Users").child(self.userName).update({"userLock" : False})
                    self.puf_auth=False
                    return call_result.DataTransferPayload(
                        status = 'Rejected',
                        data="Failed"
                    )                

        else:
            print("Database not authorized.")
            self.puf_auth=False
            return call_result.DataTransferPayload(
                    status = 'Rejected',
                    data = 'Failed'
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
        charge_req=seq_no
        if event_type=='Started' and self.db_auth and self.puf_auth and int(self.cost)>=charge_req:
            self.charge_requested = charge_req 
            self.start_transaction=True
            print("Starting Transaction")
            return call_result.TransactionEventPayload(
                total_cost = charge_req,
                charging_priority = 9
            ) 
        elif event_type=='Started' and self.db_auth and self.puf_auth:
            print("Insufficient balance. Cannot start transaction")
            self.start_transaction=False
            return call_result.TransactionEventPayload(
                total_cost = 0,
                charging_priority = -1
            ) 

        elif event_type=='Started':
            print("Authorization was unsuccessful. Cannot start transaction")
            self.start_transaction=False
            return call_result.TransactionEventPayload(
                total_cost = 0,
                charging_priority = 0
            )            

        elif event_type=='Ended':
            if self.start_transaction:
                global count
                all_users = db.child("Users").get()
                count=count+1
                certs = pem.parse_file('cert.pem')
                # subprocess.call(["node","../fabric-samples/fabcar/javascript/invoke.js", "CAR"+str(count) , str(self.charge_requested), str(certs[1]), str(timestamp), self.userName])  
                print('Transaction Ended')
                
                for user in all_users.each():
                    if user.key() == self.userName:
                        break
        
                initialCost = user.val()['chargingCost']
                db.child("Users").child(self.userName).set({"chargingCost":str(int(initialCost) - self.charge_requested), "userLock" : False})  
                self.end_time = time.time()
                time_int = self.end_time - self.start_time
                file_object = open('time_int.txt', 'a')
                file_object.write("\n")
                file_object.write(str(time_int))
                file_object.close()

                print("Remaining balance of "+self.userName+" "+str(int(initialCost) - self.charge_requested))
                self.cost='0'
                self.start_transaction=False
                self.userName=''
                self.modelName=''
                self.challenge = [0,0,0,0,0,0,0,0,0,0,0,0]
                var=self.charge_requested
                self.charge_requested=0
                self.db_auth=False
                self.puf_auth=False
                return call_result.TransactionEventPayload(
                    total_cost = var,
                    charging_priority = -9
                )

            else:
                print("Error! Transaction didn't start.")
                db.child("Users").child(self.userName).update({"userLock" : False})
                self.cost='0'
                self.start_transaction=False
                self.userName=''
                self.modelName=''
                self.challenge = [0,0,0,0,0,0,0,0,0,0,0,0]
                self.charge_requested=0
                self.db_auth=False
                self.puf_auth=False
                
                return call_result.TransactionEventPayload(
                    total_cost = self.charge_requested,
                    charging_priority = 0
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
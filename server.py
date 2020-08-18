import asyncio
import websockets
from datetime import datetime
import functools
from ocpp.routing import on
from ocpp.v20 import ChargePoint as cp
from ocpp.v20 import call_result
from myhdl import *
import pathlib
import ssl
import pyrebase
import subprocess
import pem
import random
from threading import Thread
import sys
import time
import sqlite3
import concurrent.futures
import docker

'''  For online Firebase Database(Optional) '''
# config = {
#     "apiKey": "AIzaSyAGas29t240FwqdvXjdwzz4kITTN2Ix1ro",
#     "authDomain": "charger-1eb48.firebaseapp.com",
#     "databaseURL": "https://charger-1eb48.firebaseio.com",
#     "projectId": "charger-1eb48",
#     "storageBucket": "charger-1eb48.appspot.com",
#     "messagingSenderId": "430093083458",
#     # "serviceAccount": "/home/raghav/SecureCharger/secure.json"
#     "serviceAccount": "/home/rushang99/Downloads/SecureCharger/secure.json"
# }
# firebase = pyrebase.initialize_app(config)
# auth = firebase.auth()
# email = "guptaraghav1999@gmail.com"
# password = "12345678"
# user = auth.sign_in_with_email_and_password(email,password)
# db = firebase.database()


'''  SQL Databse initialiazation '''
conn = sqlite3.connect('cars.db')


'''  Helper functions for Multi-threading  '''
count=0

def help_boot(x):
    time.sleep(x)
    return 0

def help_authorize(name):
    flag=False
    # db = firebase.database()
    # all_users = db.child("Users").get()
    # for user in all_users.each():
    #     if user.key()==name:
    #         flag=True
    #         break
    conn = sqlite3.connect('cars.db')
    cur = conn.cursor()
    cur.execute("SELECT * from USERS WHERE name='" + name + "'")
    rows = cur.fetchall()
    if len(rows)>0:
        flag  = True
        user = rows[0]


    if flag:            
        lockAcquired = user[2]
        # print(lockAcquired)
        if lockAcquired:
            print("The user is already Authorized elsewhere. Please wait and try again later!!!")  
            return [0]         
        else:     
            # Get PUF model from database (To be done later)       
            cost=user[1]
            # print(name + ' authorized successfully.')
            # print("Available balance of "+name + " " + str(cost))
            # db.child("Users").child(name).update({"userLock" : True})
            
            cur = conn.cursor()
            cur.execute("UPDATE USERS SET lock = 1 WHERE name = '"+ name+"'")
            conn.commit()
            return [1,name,cost]


    else:
        # print(name + ' not found in database.')
        return [-1]   



def help_transaction_end(userName,initialCost,charge_requested,cert, count):
    count=count+1
    # subprocess.Popen(["../../hypledger/fabric-samples/fabcar/javascript/invoke.js", "CAR"+str(count) , str(charge_requested), str(cert), str(time.time()), userName])  
    subprocess.Popen(["python3", "invoke.py", str(count)])
    print('Transaction Ended')
    conn = sqlite3.connect('cars.db')
    cur = conn.cursor()
    cur.execute("UPDATE USERS SET lock = 0, balance =" + str(int(initialCost) - charge_requested)  +" WHERE name = '"+ userName+"'")
    conn.commit()
    # db.child("Users").child(userName).set({"chargingCost":str(int(initialCost) - charge_requested), "userLock" : False})      


def help_time(start_time, auth_time, userName): 
    file_object = open('time_int.txt', 'a')
    file_object.write(userName+"-->"+str(time.time() - start_time) + "\n")
    file_object.close()
    file_object = open('time_auth.txt', 'a')
    file_object.write(userName+"-->"+str(auth_time - start_time) + "\n")
    file_object.close()


'''  ChargePoint class implementing OCPP compliant Server '''

class ChargePoint(cp):
    cost='0'
    userName=''
    modelName=''
    challenge=[0,0,0,0,0,0,0,0,0,0,0,0]
    db_auth=False
    puf_auth=False
    start_transaction=False
    charge_requested = 0
    response_compact=[]
    response_expand=[]
    time_compact=0
    time_expand=0
    start_time = 0
    auth_time = 0
    end_time = 0
        
    '''  Essential OCPP messages  '''

    # Used to notify starting of a session
    @on('BootNotification')
    async def on_boot_notitication(self, charging_station, reason, **kwargs):
        # print(charging_station['model'] + ' from ' + charging_station['vendor_name'] + ' has booted.')  
        self.start_time = time.time()     
        return call_result.BootNotificationPayload(
            current_time=datetime.utcnow().isoformat(),
            interval=10,
            status='Accepted'
        )
            
    # Server checks if car has a valid entry in Database
    @on('Authorize')
    async def on_authorize(self, id_token, **kwargs):   
        name=id_token['id_token']
        with concurrent.futures.ProcessPoolExecutor() as pool:
            fn=functools.partial(help_authorize,name)
            status = await asyncio.get_running_loop().run_in_executor(pool, fn)

        if status[0]==0:
            return call_result.AuthorizePayload(
                id_token_info = {
                    'status' : 'NotAtThisLocation',     
                },
                evse_id = [int(self.cost)]
            )

        elif status[0]==1:
            self.cost=status[2]
            self.userName=status[1]
            self.db_auth=True
            self.auth_time = time.time()
            return call_result.AuthorizePayload(
                id_token_info = {
                    'status' : 'Accepted',     
                },
                evse_id = [int(self.cost)]
            )
        elif status[0]==-1:
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
                },
                evse_id = [0]
            ) 
    # Communication for PPUF authorization
    @on('DataTransfer')
    def data_transfer(self,data,vendor_id,**kwargs):
        if(self.db_auth):
            if(str(data)=="Request Challenge"):
                #Generate Challenge                
                n=random.randrange(0,4096,1)
                bn=str(bin(n).replace("0b",""))
                self.challenge=[0,0,0,0,0,0,0,0,0,0,0,0]
                for i in range(len(bn)):
                    self.challenge[12-len(bn)+i]=(ord(bn[i])-ord('0'))
                print(self.userName+"--> Challenge Generated-- " + str(self.challenge))
                                
                # import fexpand as fe
                # start_time = time.time()
                # self.response_expand=fe.expand(self.challenge)
                # self.time_expand=(time.time() - start_time)

                # Request model from database and generate response
                output=subprocess.Popen( ['python3', 'test_expand.py', str(self.challenge)], stdout=subprocess.PIPE ).communicate()[0]
                arr=str(output).split("\\n")
                response=arr[1].split()[:4]
                for i in range(4):
                    response[i]=int(response[i])
                self.response_expand=response
                self.time_expand=float(arr[2])

                return call_result.DataTransferPayload(
                    status = 'Rejected',
                    data=self.challenge
                )
            elif(str(vendor_id)=="Challenge Sent"):
                # print(self.userName+"--> Response recorded--"+str(self.challenge))    
                self.response_compact=data[:4]
                self.time_compact=data[4]
                # if (time_compact < time_expand) and time_compact<1e-4  and time_expand > 1e-5 and self.response_compact==self.response_expand:
                if self.response_compact==self.response_expand:
                    # print("time_expand--"+str(self.time_expand))
                    # print("time_compact--"+str(self.time_compact))
                    # print(self.userName+"--> PUF authorization successful--"+str(self.challenge))
                    self.puf_auth=True
                    return call_result.DataTransferPayload(
                        status = 'Accepted',
                        data="Done"
                    )
                else:
                    # print("time_expand--"+str(self.time_expand))
                    # print("time_compact--"+str(self.time_compact))
                    # print(self.userName+"--> PUF authorization unsuccessful--"+str(self.challenge))
                    # db.child("Users").child(self.userName).update({"userLock" : False})
                    self.puf_auth=False
                    return call_result.DataTransferPayload(
                        status = 'Rejected',
                        data="Failed"
                    )                

        else:
            # print("Database not authorized.")
            self.puf_auth=False
            return call_result.DataTransferPayload(
                    status = 'Rejected',
                    data = 'Failed'
                )

    # Transaction begin communication (only after successful authentication)
    @on('TransactionEvent')
    async def transaction_event(self, event_type, timestamp, trigger_reason, seq_no, transaction_data, **kwargs):
        charge_req=seq_no
        if event_type=='Started' and self.db_auth and self.puf_auth and int(self.cost)>=charge_req:
            self.charge_requested = charge_req 
            self.start_transaction=True
            # print("Starting Transaction")
            return call_result.TransactionEventPayload(
                total_cost = charge_req,
                charging_priority = 9
            ) 
        elif event_type=='Started' and self.db_auth and self.puf_auth:
            # print("Insufficient balance. Cannot start transaction")
            self.start_transaction=False
            return call_result.TransactionEventPayload(
                total_cost = 0,
                charging_priority = -1
            ) 

        elif event_type=='Started':
            # print("Authorization was unsuccessful. Cannot start transaction")
            self.start_transaction=False
            return call_result.TransactionEventPayload(
                total_cost = 0,
                charging_priority = 0
            )            

        elif event_type=='Ended':
            if self.start_transaction:
                global count
                count+=1
                certs = pem.parse_file('cert.pem')
                certs[1]=" "
                with concurrent.futures.ProcessPoolExecutor() as pool:
                    fn=functools.partial(help_transaction_end,self.userName,self.cost,self.charge_requested,certs[1], count)
                    status1 = await asyncio.get_running_loop().run_in_executor(pool, fn)
                
                
                with concurrent.futures.ProcessPoolExecutor() as pool:
                    fn=functools.partial(help_time, self.start_time, self.auth_time, self.userName)
                    status2 = await asyncio.get_running_loop().run_in_executor(pool, fn)


                # print("Remaining balance of "+self.userName+" "+str(int(self.cost) - self.charge_requested))
                self.cost='0'
                self.start_transaction=False
                self.userName=''
                self.modelName=''
                self.challenge = [0,0,0,0,0,0,0,0,0,0,0,0]
                var=self.charge_requested
                self.charge_requested=0
                self.db_auth=False
                self.puf_auth=False
                self.response_compact=[]
                self.response_expand=[]
                self.time_compact=0
                self.time_expand=0
                self.start_time = 0
                self.end_time = 0
                return call_result.TransactionEventPayload(
                    total_cost = var,
                    charging_priority = -9
                )

            else:
                # print("Error! Transaction didn't start.")
                # db.child("Users").child(self.userName).update({"userLock" : False})
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


''' Other OCPP messages  '''

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

    @on('ClearCache')
    async def clear_cache(self):
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

async def on_connect(websocket, path):
    """ For every new charge point that connects, create a ChargePoint instance
    and start listening for messages.

    """
    charge_point_id = path.strip('/')
    cp = ChargePoint(charge_point_id, websocket)
    await cp.start()
    
    
'''  Setup for Secure websockets over TLS  '''
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain("cert.pem")

async def main():
    try:
        server = await websockets.serve(
            on_connect,
            '0.0.0.0',
            9000,
            subprotocols=['ocpp2.0'],
            ssl=ssl_context,
            ping_timeout=1000000000000      
        )

        await server.wait_closed()
    except Exception:
        print("Exception")

if __name__ == '__main__':
    asyncio.run(main())
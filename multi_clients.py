from subprocess import call 
for i in range(0, 10):
    call(['gnome-terminal', '-e', "python3 ocpp_client.py car" + str(i)+ ".json"])

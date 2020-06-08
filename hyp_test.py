import docker
import subprocess
import sys
import time
client = docker.from_env()
cli = client.containers.get('cli')
start_time = time.time()
cli.exec_run("peer chaincode invoke -o orderer.example.com:7050 --tls true --cafile /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem -C mychannel -n mycc --peerAddresses peer0.org1.example.com:7051 --tlsRootCertFiles /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt --peerAddresses peer0.org2.example.com:9051 --tlsRootCertFiles /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/ca.crt -c '{"+'"function":"CreateCar","Args":["CAR'+str(sys.argv[1])+'","Raghav","roadster","sdfa","abcd123","sjdf"]}'+"'")
file_object = open('hyp_time.txt', 'a')
file_object.write(str(sys.argv[1])+"-->"+str(time.time() - start_time) + "\n")
file_object.close()
print("Done")
sys.exit(0)
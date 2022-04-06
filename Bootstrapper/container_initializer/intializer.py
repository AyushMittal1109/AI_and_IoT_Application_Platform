import paramiko
import json
import os
import time
from flask import Flask , request
from pymongo import MongoClient
from azure.mgmt.compute import ComputeManagementClient
from azure.storage.fileshare import ShareFileClient
from azure.storage.fileshare import ShareDirectoryClient
from azure.storage.fileshare import ShareClient
# app = Flask(__name__)
# app.config['SECRET_KEY'] = 'secretkey'

CONNECTION_STRING = "mongodb://root:root@cluster0-shard-00-00.llzhh.mongodb.net:27017,cluster0-shard-00-01.llzhh.mongodb.net:27017,cluster0-shard-00-02.llzhh.mongodb.net:27017/myFirstDatabase?ssl=true&replicaSet=atlas-u1s4tk-shard-0&authSource=admin&retryWrites=true&w=majority"
client = MongoClient(CONNECTION_STRING)
dbname = client['nodeManager']
connection_string = "DefaultEndpointsProtocol=https;AccountName=storageias;AccountKey=tnxGtqqFpuRfoJMxRR7H5evonZ0P+2dZVoV+VSTHKqOSyxkMIihIUMsXQ7KM+eLguN2/b8ncl3S9+AStZRvImg==;EndpointSuffix=core.windows.net"
file_client = ShareClient.from_connection_string(conn_str=connection_string,share_name="testing-file-share",file_path="uploaded_file.py")
share_name="testing-file-share"

app = dbname["node"]

f = open('./Bootstrapper/subscription_config.json')
subs = json.load(f)
subscription_id = subs["id"]
credentials = subs["credentials"]

f1 = open('./Bootstrapper/vm_user_config.json')
vm_user = json.load(f1)
f2 = open('./Bootstrapper/vm_details.json')
vm_details = json.load(f2)
f3 = open('./Bootstrapper/container_initializer/bootstrap_initializer_config.json')
initialize_details = json.load(f3)

def initialize_env(s,vm_ip):

    build_cmd = "pip3"
    stdin,stdout,stderr = s.exec_command(build_cmd)
    lines = stdout.readlines()
    print(lines)

    if len(lines)<=10:
        build_cmd = "sudo apt install python3-pip"
        stdin,stdout,stderr = s.exec_command(build_cmd)
        lines = stdout.readlines()
        print(lines)
    else:
        print("python3-pip Present!")

    build_cmd = "pip install azure-storage-file-share"
    stdin,stdout,stderr = s.exec_command(build_cmd)
    lines = stdout.readlines()
    print(lines)

    build_cmd = "pip install azure-storage-file-share"
    stdin,stdout,stderr = s.exec_command(build_cmd)
    lines = stdout.readlines()
    print(lines)

def initialize_docker_env(s,vm_ip):

    build_cmd = "docker -v"
    stdin,stdout,stderr = s.exec_command(build_cmd)
    lines = stdout.readlines()
    print(lines)

    if len(lines)==0:
        build_cmd = "curl -fsSL https://get.docker.com -o get-docker.sh"
        stdin,stdout,stderr = s.exec_command(build_cmd)
        lines = stdout.readlines()
        print(lines)

        buil_cmd = "sh get-docker.sh"
        stdin,stdout,stderr = s.exec_command(buil_cmd)
        lines = stdout.readlines()
        print(lines)

        buil_cmd = "curl -fsSL https://test.docker.com -o test-docker.sh"
        stdin,stdout,stderr = s.exec_command(buil_cmd)
        lines = stdout.readlines()
        print(lines)

        buil_cmd = "sh test-docker.sh" 
        stdin,stdout,stderr = s.exec_command(buil_cmd)
        lines = stdout.readlines()
        print(lines)
        
        buil_cmd = "sh install.sh" 
        stdin,stdout,stderr = s.exec_command(buil_cmd)
        lines = stdout.readlines()
        print(lines)

        buil_cmd = "docker -v" 
        stdin,stdout,stderr = s.exec_command(buil_cmd)
        lines = stdout.readlines()
        print(lines)
    else:
        print("Docker Environment Present!")

def upload_container(s,service_name,vm_ip,source,destination,source_path,folder_name):

    sftp_client = s.open_sftp()

    localfolder = source
    basefolder = destination

    command="ls"
    stdin,stdout,stderr =s.exec_command(command)
    lines = stdout.readlines()   
    print(lines)
    flag = False
    for i in lines:
        print(i[:-1])
        if service_name == i[:-1]:
            flag = True
            break;
    
    if flag == False:
        sftp_client.put('./Bootstrapper/container_initializer/download_code_base.py' , './download_code_base.py')
        time.sleep(1)
        command="python3 download_code_base.py '"+source_path+"' '"+ folder_name +"'"
        stdin,stdout,stderr =s.exec_command(command)
        lines = stdout.readlines()   
        print(lines)
        time.sleep(1)
        # command="sudo rm download_code_base.py"
        # stdin,stdout,stderr =s.exec_command(command)
        # lines = stdout.readlines()   
        # print(lines)
        
        # for path,dirs,files in os.walk(localfolder):
        #     if path.lstrip(localfolder)!=None:       
        #         extrapath=path.split(basefolder)[-1]   
        #         command="cd root"  
        #         stdin,stdout,stderr = client.exec_command(command)
        #         command="mkdir {}".format(extrapath)
        #         client.exec_command(command)
        #         lines = stdout.readlines()   
        #         print(lines)
                
        #     for file in files:  
        #         filepath=os.path.join(path,file)
        #         extrapath=path.split(basefolder)[-1]
        #         command="cd root"  
        #         stdin,stdout,stderr = client.exec_command(command)
        #         sftp_client.put(filepath,"{}/{}".format(extrapath,file))
    else:
        print(service_name+" Dir already Present")

    sftp_client.close()

def initialize_container(s,service_name,vm_ip,path):

    buil_cmd = "[[docker images -q {"+service_name.lower()+"}]]|| echo 1"
    #buil_cmd = "[[docker ps -q -f name={"+service_name.lower()+"}]] || echo 1"
    stdin,stdout,stderr = s.exec_command(buil_cmd)
    lines = stdout.readlines()
    print(lines)

    # if lines[0]!='1\n':
    buil_cmd = "sudo systemctl start docker" 
    stdin,stdout,stderr = s.exec_command(buil_cmd)
    lines = stdout.readlines()
    print(lines)

    buil_cmd = "sudo systemctl enable docker" 
    stdin,stdout,stderr = s.exec_command(buil_cmd)
    lines = stdout.readlines()
    print(lines)

    buil_cmd = "sudo systemctl status docker" 
    stdin,stdout,stderr = s.exec_command(buil_cmd)
    lines = stdout.readlines()
    print(lines)

    buil_cmd = "sudo docker info" 
    stdin,stdout,stderr = s.exec_command(buil_cmd)
    lines = stdout.readlines()
    print(lines)
    
    buil_cmd = "sudo docker build -t "+ service_name.lower() + " " + path
    stdin,stdout,stderr = s.exec_command(buil_cmd)
    lines = stdout.readlines()
    print(lines)

def start_container(s,service_name,vm_ip,port):

    buil_cmd = "[[docker ps -q -f name={"+service_name.lower()+"}]] || echo 1"
    stdin,stdout,stderr = s.exec_command(buil_cmd)
    lines = stdout.readlines()
    print(lines)
    
    #if lines[0]!='1\n':
    if True :
        run_cmd = "sudo docker run -p "+ str(port)+":5000 "+ service_name.lower()
        s.exec_command(run_cmd)
        print("Starting Container....")
    else:
        print("VM already Up and running")


def restart_vm(GROUP_NAME,VM_NAME):
    compute_client = ComputeManagementClient(credentials, subscription_id)
    async_vm_restart = compute_client.virtual_machines.restart(
            GROUP_NAME, VM_NAME)
    async_vm_restart.wait()
    pass

# for key in initialize_details:
# initialize_docker_env("VM2")
# upload_container("Authentication_Manager",5001, "VM2","./Authentication_Manager/","~/Authentication_Manager/")
# initialize_container("Authentication_Manager",5001, "VM2","./Authentication_Manager/","~/Authentication_Manager/")
# start_container("Authentication_Manager",5001, "VM2","./Authentication_Manager/","~/Authentication_Manager/")
#upload_container("Request_Manager",5000, "VM2","./Request_Manager/","~/Request_Manager/")
#initialize_containers("Request_Manager",5000, "VM1","./Request_Manager/","~/Request_Manager/")

# @app.route('/Initialize_Environment',methods = ['POST'])
def init():
    vm_ip = request.get_json()['vm_ip']
    initialize_docker_env(s,vm_ip)

# @app.route('/Upload',methods = ['POST'])
def upload():
    vm_ip = request.get_json()['vm_ip']
    source = request.get_json()['source']
    destination = request.get_json()['destination']
    upload_container(s,vm_ip,source,destination)

# @app.route('/Containerize',methods = ['POST'])
def containerize():
    service_name = request.get_json()['service_name']
    vm_ip = request.get_json()['vm_ip']
    path = request.get_json()['path']
    initialize_container(s,service_name,vm_ip,path)

# @app.route('/Deploy',methods = ['POST'])
def deploy():
    service_name = request.get_json()['service_name']
    vm_ip = request.get_json()['vm_ip']
    port = request.get_json()['port']
    start_container(s,service_name,vm_ip,port)

# @app.route('/restart',methods = ['POST'])
def restart():
    service_ip = request.get_json()['Server_ip']
    username = request.get_json()['username']
    password = request.get_json()['password']
    #restart_vm(service_ip,vm_ip,port)
    app.updtae_one({"ip":service_ip},{"$set":{"status": "active"}})


if(__name__ == '__main__'):   
    
    #client.connect("20.213.161.182", 22, "IASHackathon1", "IASHackathon1")
    #client.connect("20.216.18.166", 22, username =  "azureuser", password = "@mazingSpiderMan",allow_agent=True,look_for_keys = False)
    for key in initialize_details:
        vm_ip = vm_details[initialize_details[key]["vm_name"]]["ip"]
        source = initialize_details[key]["source"]
        destination = initialize_details[key]["destination"]
        source_path = initialize_details[key]["source_path"]
        folder_name = initialize_details[key]["folder_name"]
        service_name = key
        path = destination
        port = initialize_details[key]["port"]
        username = vm_details[initialize_details[key]["vm_name"]]["username"]
        password = vm_details[initialize_details[key]["vm_name"]]["password"]
        
        s = paramiko.SSHClient()
        s.load_system_host_keys()
        s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        s.connect(vm_ip, 22, username , password)

        initialize_env(s,vm_ip)
        initialize_docker_env(s,vm_ip)
        upload_container(s,service_name,vm_ip,source,destination,source_path,folder_name)
        time.sleep(10)
        initialize_container(s,service_name,vm_ip,path)
        time.sleep(20)
        start_container(s,service_name,vm_ip,port)
        print(key + " Deployed")
    
    # app.run(host ='127.0.0.1',port=8000,debug=True)
import os
import getpass
import django
import psycopg2
import requests
import socket
import itertools
import difflib
import time
import schedule
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from sys import platform
from KlAkOAPI.Params import KlAkParams, KlAkArray
from KlAkOAPI.AdmServer import KlAkAdmServer
from KlAkOAPI.SrvView import KlAkSrvView
from KlAkOAPI.HostGroup import KlAkHostGroup
from KlAkOAPI.InventoryApi import KlAkInventoryApi
from KlAkOAPI.ChunkAccessor import KlAkChunkAccessor
from django.db import connection, connections, transaction
from django.utils.timezone import make_aware
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project.settings')
django.setup()

from software.models import *

username = getpass.getpass("Введите логин: ")
password = getpass.getpass("Введите пароль: ")

Host.objects.all().delete()
Installation.objects.all().delete()
ProgramData.objects.all().delete()

def is_server_available(host, port):
    try:
        socket.create_connection((host, port), timeout=1)
        return True
    except socket.error:
        return False

def get_server(server_ip, server_port):
    server_url = 'https://' + server_ip + ':' + str(server_port)
    return KlAkAdmServer.Create(server_url, username, password, verify=False)

def get_chunk(accessor, start, step, chunk_accessor):
    return chunk_accessor.GetItemsChunk(accessor, start, step)

def get_items_count(accessor, chunk_accessor):
    return chunk_accessor.GetItemsCount(accessor).RetVal()


def InsertData(data, inspection_id):
    aware_datetime = make_aware(data['tmFirstAppear'])
    existing_data = ProgramData.objects.filter(inspection_id=inspection_id, productid=data['strID']).first()
    if existing_data is None: #Если данных нет в базе, то добавить
        ProgramData.objects.create(
            productid=data['strID'],
            inspection_id=inspection_id,
            name=data['wstrDisplayName'],
            version=data['wstrDisplayVersion'],
            publisher=data['wstrPublisher'],
            comments=data['wstrComments'],
            arpregkey=data['wstrARPRegKey'],
            hostcount=data['nHostCount'],
            tmfirstappear=aware_datetime,
            bismsi=data['bIsMsi'],
            directory_id=None
        )

    elif existing_data.hostcount != data['nHostCount'] : #Если данные существуют и не имеют устаревших значений, то обновить hostcount
        existing_data.hostcount = data['nHostCount']
        existing_data.save()
    return None


def InsertHost(hostname_list, inspection_id):
    # Get the inspection object
    inspection = Inspection.objects.get(id=inspection_id)

    # Create a list to hold the new Host objects
    new_hosts = []

    for hostname in hostname_list:
        # Check if the host already exists
        existing_host = Host.objects.filter(hostname=hostname, inspection=inspection).first()

        if existing_host is None:
            # If the host does not exist, create a new host object
            new_hosts.append(Host(hostname=hostname, inspection=inspection))

    # Use bulk_create to create all the new Host objects at once
    Host.objects.bulk_create(new_hosts)


def InsertProgram(hostname, inspection_id, ProductID, InstallDate, InstallDir):
    inspection = Inspection.objects.get(id=inspection_id)
    host = Host.objects.filter(hostname=hostname).first()
    program_data = ProgramData.objects.filter(productid=ProductID, inspection=inspection).first()

    installation = None 

    if InstallDate:
        naive_datetime = datetime.strptime(InstallDate + "000000", "%Y%m%d%H%M%S")
        aware_datetime = make_aware(naive_datetime)
        existing_installation = Installation.objects.filter(host=host, programdata=program_data, installdir=InstallDir, installdate=aware_datetime).first()
    else:
        existing_installation = Installation.objects.filter(host=host, programdata=program_data, installdir=InstallDir).first()

    if existing_installation is None:
        if program_data is not None:
            if InstallDate:
                installation = Installation(host=host, programdata=program_data, installdir=InstallDir, installdate=aware_datetime)
            else:
                installation = Installation(host=host, programdata=program_data, installdir=InstallDir)

    return installation
    



def DeleteData(strIDs, inspection_id):
    ProgramData.objects.exclude(productid__in=strIDs).filter(inspection_id=inspection_id).delete()


def DeleteHost(hostnames, inspection_id):
    Host.objects.exclude(hostname__in=hostnames).filter(inspection_id=inspection_id).delete()


def DeleteHostProgram(hostname, productids):
    host = Host.objects.filter(hostname=hostname).first()
    Installation.objects.exclude(programdata__productid__in=productids).filter(host__hostname=hostname).delete()


def GetHostProgram(hostname, hostnameID, inspection_id, server_ip, server_port):
    try:
        server = get_server(server_ip, server_port)
        inventory = KlAkInventoryApi(server)
        productids = []
        installations = []
        programInfo = inventory.GetHostInvProducts(hostnameID, pParams = {'KLEVP_EA_PARAM_1' : True}).RetVal()
        for product in programInfo['GNRL_EA_PARAM_1']:
            installation = InsertProgram(hostname, inspection_id, product['ProductID'], product['InstallDate'], product['InstallDir'])
            if installation is not None: 
                installations.append(installation)
                productids.append(product['ProductID'])
        DeleteHostProgram(hostname, productids)
        Installation.objects.bulk_create(installations)
    except Exception as e:
        print(f"Произошла ошибка при вставке данных для {hostname}: {e}")


def GetHost(server, inspection_id):
    hostGroup = KlAkHostGroup(server)
    strAccessor = hostGroup.FindGroups(None, ['id', 'name'], [], {'KLGRP_FIND_FROM_CUR_VS_ONLY': True}, lMaxLifeTime=60 * 60 * 3).OutPar('strAccessor')
    groupStart = 0
    groupStep = 100
    groupChunkAccessor = KlAkChunkAccessor(server)
    groupCount = get_items_count(strAccessor, groupChunkAccessor)
    hostname_list = []
    hostnameID_list = []
    while groupStart < groupCount:
        groupChunk = get_chunk(strAccessor, groupStart, groupStep, groupChunkAccessor)
        parGroups = groupChunk.OutPar('pChunk')['KLCSP_ITERATOR_ARRAY']
        for oObj in parGroups:
            strAccessor = hostGroup.FindHosts('(&(KLHST_INSTANCEID <> \"\")(KLHST_WKS_GROUPID = ' + str(oObj['id']) + '))', ['KLHST_WKS_HOSTNAME', 'KLHST_WKS_DN'], [], {'KLGRP_FIND_FROM_CUR_VS_ONLY': True}, lMaxLifeTime=60 * 60 * 3).OutPar('strAccessor')
            hostStart = 0
            hostStep = 100
            hostChunkAccessor = KlAkChunkAccessor(server)
            hostCount = get_items_count(strAccessor, hostChunkAccessor)
            while hostStart < hostCount:
                hostChunk = hostChunkAccessor.GetItemsChunk(strAccessor, hostStart, hostStep)
                parHosts = hostChunk.OutPar('pChunk')['KLCSP_ITERATOR_ARRAY']
                for oObj in parHosts:
                    hostname_list.append(oObj['KLHST_WKS_DN'])
                    hostnameID_list.append(oObj['KLHST_WKS_HOSTNAME'])
                hostStart += hostStep
        groupStart += groupStep
    DeleteHost(hostname_list, inspection_id)
    InsertHost(hostname_list, inspection_id)

    return hostname_list, hostnameID_list


def GetProgram(server, inspection_id):
    try:
        oSrvView = KlAkSrvView(server)
        oFields2Return = KlAkArray(['nId','strID','wstrDisplayName','wstrDisplayVersion','wstrPublisher','wstrComments','wstrARPRegKey','nHostCount','tmFirstAppear','bIsMsi'])
        oField2Order = KlAkArray([{'Name': 'nId', 'Asc': True}])
        wstrIteratorId = oSrvView.ResetIterator('InvSrvViewName', '', oFields2Return, oField2Order, {}, lifetimeSec = 60 * 60 * 3).OutPar('wstrIteratorId')
        iRecordCount = oSrvView.GetRecordCount(wstrIteratorId).RetVal()
        iStep = 200
        iStart = 0
        strIDs = []
        while iStart < iRecordCount:
            pRecords = oSrvView.GetRecordRange(wstrIteratorId, iStart, iStart + iStep).OutPar('pRecords')
            for oObj in pRecords['KLCSP_ITERATOR_ARRAY']:
                data = {'strID': oObj['strID'], 'wstrDisplayName': oObj['wstrDisplayName'], 'wstrDisplayVersion': oObj['wstrDisplayVersion'], 'wstrPublisher': oObj['wstrPublisher'],'wstrComments': oObj['wstrComments'], 'wstrARPRegKey': oObj['wstrARPRegKey'], 'nHostCount': oObj['nHostCount'],'tmFirstAppear': oObj['tmFirstAppear'], 'bIsMsi': oObj['bIsMsi']}
                InsertData(data, inspection_id)
                strIDs.append(oObj['strID'])
            iStart += iStep + 1
        DeleteData(strIDs, inspection_id)
        oSrvView.ReleaseIterator(wstrIteratorId)
    except Exception as e:
        print('Ошибка:', e)


def pool_GetProgram(inspection, server_port):
    start_time = time.time()

    server_ip = inspection.ip
    inspection_id = inspection.id

    if not is_server_available(server_ip, server_port):
        print(f'Сервер {server_ip} недоступен')
        return

    server = get_server(server_ip, server_port)
    
    print(f'{server_ip} Запуск потока ')

    GetProgram(server, inspection_id)  

    data_objects = ProgramData.objects.filter(inspection__id = inspection_id)
    directory_objects = Directory.objects.all()

    for data_object in data_objects:
        directory_objects = Directory.objects.filter(name__contains=data_object.name)
        for directory_object in directory_objects:
            data_object.directory_id = directory_object.id
            data_object.save()    

    end_time = time.time()
    print(f'{server_ip} Время выполнения GetProgram: {end_time - start_time} секунд')

def pool_GetHost(inspection, server_port):
    start_time = time.time()

    server_ip = inspection.ip
    inspection_id = inspection.id

    if not is_server_available(server_ip, server_port):
        print(f'Сервер {server_ip} недоступен')
        return

    server = get_server(server_ip, server_port)
    
    print(f'{server_ip} Запуск потока ')
        
    hostname_list, hostnameID_list = GetHost(server, inspection_id)

    with ThreadPoolExecutor(max_workers=90) as executor:
        executor.map(lambda hostname, hostnameID : GetHostProgram(hostname, hostnameID, inspection_id, server_ip, server_port), hostname_list, hostnameID_list)

    end_time = time.time()
    print(f'{server_ip} Время выполнения GetHost: {end_time - start_time} секунд')
    
def main():
    inspection_list = Inspection.objects.order_by('id')
    server_port = 13299
    try:
        with ThreadPoolExecutor(max_workers=90) as executor:
            executor.map(lambda inspection: pool_GetProgram(inspection, server_port), inspection_list)
        with ThreadPoolExecutor(max_workers=90) as executor:
            executor.map(lambda inspection: pool_GetHost(inspection, server_port), inspection_list)
    except Exception as e:
        print('Ошибка:', e)

if __name__ == '__main__':
    main()




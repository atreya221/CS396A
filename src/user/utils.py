from .models import User
from pandas import read_csv
import os
from src import settings
from django.shortcuts import render, redirect, HttpResponseRedirect
from re import M
from django.contrib import messages
import bcrypt
from netaddr import IPNetwork, IPSet

# make new hashed password
def MAKE_PASSWORD(password):
    password = password.encode()
    hash = bcrypt.hashpw(password, bcrypt.gensalt())
    return hash.decode()


# match password to hashed one
def CHECK_PASSWORD(password, hash):
    return bcrypt.checkpw(password.encode(), hash.encode())


# check if user is already logged in or not
def IsLoggedIn(request):
    if request.session.has_key("username"):
        try:
            user = User.objects.get(username=request.session["username"])
            return user
        except:
            return None
    else:
        return None

def view_public_subnets(file):
    file_path = os.path.join(settings.MEDIA_ROOT, file.file.name)
    public_subnets = []
    try:
        print(f'opening file: {file_path}')
        csvFile = read_csv(file_path)
        for entry in csvFile["Subnet"]:
            #print(entry.strip())
            if not IPNetwork(entry.strip().replace("'", "")).is_private():
                #print(entry.strip().replace("'", ""))
                public_subnets.append(entry.replace("'", ""))
        location_cnt = len(set(list(csvFile["Location"])))
    except Exception as e:
        print(e)
    return len(csvFile), location_cnt, public_subnets

def remove_public_subnets(file):
    file_path = os.path.join(settings.MEDIA_ROOT, file.file.name)
    public_subnets_id = []
    try:
        print(f'opening file: {file_path}')
        csvFile = read_csv(file_path)
        for i in range(len(csvFile)):
            #print(entry.strip())
            if not IPNetwork(csvFile["Subnet"].iloc[i].strip().replace("'", "")).is_private():
                #print(csvFile["Subnet"].iloc[i].strip().replace("'", ""))
                public_subnets_id.append(i)
    except Exception as e:
        print(e)


    with open(file_path) as original_file:
        subnets_list = original_file.readlines()

    modified_subnets_list = []
    for i in range(len(subnets_list)):
        if (i-1) not in public_subnets_id:
            modified_subnets_list.append(subnets_list[i])

    try:
        with open(file_path, 'w') as outfile:
            outfile.writelines(modified_subnets_list)
    except Exception as e:
        print(e)

def view_self_conflicts(file):
    file_path = os.path.join(settings.MEDIA_ROOT, file.file.name)
    csvFile = read_csv(file_path)
    locsub = []
    for i in range(len(csvFile)):
        locsub.append(
            str(i) + "_" + 
            str(csvFile["Location"].iloc[i].replace("'", "").strip()) + "_" + 
            str(csvFile["Subnet"].iloc[i].replace("'", "").strip())
        )
    overlapped_subnets = set()
    overlapping = set()

    for i in locsub:
        for j in locsub:
            if i == j:
                continue
            else:
                id1, loc1, sub1 = i.split("_")
                id2, loc2, sub2 = j.split("_")
                if loc1 == loc2:
                    continue
                #print(id1, loc1, sub1)
                #print(id2, loc2, sub2)
                if IPSet(IPNetwork(sub1)) & IPSet(IPNetwork(sub2)):
                    node1 = i
                    node2 = j
                    overlapped_subnets.add(node1)
                    overlapped_subnets.add(node2)
                    
                    tmp = tuple()
                    if IPNetwork(sub1).size == IPNetwork(sub2).size:
                        if int(loc1) < int(loc2):
                            tmp = (node1, node2)
                        else:
                            tmp = (node2, node1)
                    elif IPNetwork(sub1).size < IPNetwork(sub2).size:
                        tmp = (node1, node2)
                    else:
                        tmp = (node2, node1)
                    overlapping.add(tmp)
    return [overlapping, overlapped_subnets]


def remove_self_conflicts(file):
    return None
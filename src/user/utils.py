from .models import User
from .wis import wis_lp
import csv
from pandas import read_csv
import os
import math
from src import settings
from django.shortcuts import render, redirect, HttpResponseRedirect
from re import M
from django.contrib import messages
import bcrypt
import random
import networkx as nx
from netaddr import IPNetwork, IPSet, IPAddress, spanning_cidr

# Global hyperparameters
TYPE_1_COST = 1
TYPE_2_COST = 2
TYPE_3_COST = 10
ALFA = 1000
BETA = 2000


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

def write_to_csv(fname, mydict):
    writer = csv.writer(open(fname, 'w'))
    for key, value in mydict.items():
        writer.writerow([key, value])

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
    overlapped_subnets_id = [[j.replace("'", "") for j in i.split("_")] for i in list(overlapped_subnets)]
    overlapping_id = [[j.split("_")[1:] for j in list(i)] for i in list(overlapping)]
    return [overlapping, overlapped_subnets, overlapped_subnets_id, overlapping_id]


def remove_self_conflicts(file):
    file_path = os.path.join(settings.MEDIA_ROOT, file.file.name)
    overlapping, overlapped_subnets, _, _ = view_self_conflicts(file)
    overlapped_subnets_id = [int(i.split("_")[0]) for i in overlapped_subnets]
    print(overlapped_subnets_id)

    with open(file_path) as original_file:
        subnets_list = original_file.readlines()

    modified_subnets_list = []
    for i in range(len(subnets_list)):
        if (i-1) not in overlapped_subnets_id:
            modified_subnets_list.append(subnets_list[i])

    try:
        with open(file_path, 'w') as outfile:
            outfile.writelines(modified_subnets_list)
    except Exception as e:
        print(e)


def view_merge_conflicts(file1, file2):
    filePath1 = os.path.join(settings.MEDIA_ROOT, file1.file.name)
    filePath2 = os.path.join(settings.MEDIA_ROOT, file2.file.name)
    csvFile1 = read_csv(filePath1)
    csvFile2 = read_csv(filePath2)
    locsub1 = []
    locsub2 = []
    for i in range(len(csvFile1)):
        locsub1.append(
            str(csvFile1["Location"].iloc[i].replace("'", "").strip()) + "_" + 
            str(csvFile1["Subnet"].iloc[i].replace("'", "").strip())
        )
    for i in range(len(csvFile2)):
        locsub2.append(
            str(csvFile2["Location"].iloc[i].replace("'", "").strip()) + "_" + 
            str(csvFile2["Subnet"].iloc[i].replace("'", "").strip())
        )
    overlapping = set()

    for i in locsub1:
        for j in locsub2:
            if i == j:
                continue
            else:
                loc1, sub1 = i.split("_")
                loc2, sub2 = j.split("_")
                if loc1 == loc2:
                    continue

                if IPSet(IPNetwork(sub1)) & IPSet(IPNetwork(sub2)):
                    node1 = i
                    node2 = j
                    
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
    return overlapping


def remove_merge_conflicts(file1, file2, MERGING_FRACTION):
    filePath1 = os.path.join(settings.MEDIA_ROOT, file1.file.name)
    filePath2 = os.path.join(settings.MEDIA_ROOT, file2.file.name)
    csvFile1 = read_csv(filePath1)
    csvFile2 = read_csv(filePath2)
    locsubdict1 = {}
    locsubdict2 = {}
    for i in range(len(csvFile1)):
        try:
            locsubdict1[str(csvFile1["Location"].iloc[i].replace("'", "").strip())].append(str(csvFile1["Subnet"].iloc[i].replace("'", "").strip()))
        except:
            locsubdict1[str(csvFile1["Location"].iloc[i].replace("'", "").strip())] = [str(csvFile1["Subnet"].iloc[i].replace("'", "").strip())]

    for i in range(len(csvFile2)):
        try:
            locsubdict2[str(csvFile2["Location"].iloc[i].replace("'", "").strip())].append(str(csvFile2["Subnet"].iloc[i].replace("'", "").strip()))
        except:
            locsubdict2[str(csvFile2["Location"].iloc[i].replace("'", "").strip())] = [str(csvFile2["Subnet"].iloc[i].replace("'", "").strip())]

    E1_routes=dict(sorted(locsubdict1.items(), key=lambda item: len(item[1]), reverse=True)[0:int(len(locsubdict1)*MERGING_FRACTION)])
    E2_routes=dict(sorted(locsubdict2.items(), key=lambda item: len(item[1]), reverse=True)[0:int(len(locsubdict2)*MERGING_FRACTION)])
    all_routes = {}
    all_routes.update(E1_routes)
    all_routes.update(E2_routes)

    gen_random_values_for_addr_types({**E1_routes, **E2_routes})

    conflict_edges = view_merge_conflicts(file1, file2)
    if len(conflict_edges) > 0:
        G = create_conflict_graph(conflict_edges)
        subnets_to_keep, subnets_to_change = wis_lp(G)
        if len(subnets_to_change) > 0:
            all_routes_modified = remove_subnets_to_be_changed(all_routes, subnets_to_change)
    new_coalition = merge_split_process(all_routes_modified)
    new_conflict_edges = find_coalition_overlaps(new_coalition)
    G_ = create_conflict_graph(new_conflict_edges)
    to_keep, to_change = wis_lp(G_)
    print (len(to_change))
    print (to_change)
    return [to_keep, to_change]

def find_coalition_overlaps(routes):
    locsub = []
    for key, values in routes.items():
        for value in values:
            locsub.append(
                str(key.replace("'", "").strip()) + "_" + 
                str(value).replace("'", "").strip()
            )
    overlapping = set()

    for i in locsub:
        for j in locsub:
            if i == j:
                continue
            else:
                loc1, sub1 = i.split("_")
                loc2, sub2 = j.split("_")

                if IPSet(IPNetwork(sub1)) & IPSet(IPNetwork(sub2)):
                    node1 = i
                    node2 = j
                    
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
    return overlapping



def merge(ip_addrs, N):
    if not hasattr(ip_addrs, '__iter__'):
        raise ValueError('A sequence or iterator is expected!')

    ranges = []

    for ip in ip_addrs:
        cidr = IPNetwork(ip)
        # Since non-overlapping ranges are the common case, remember the original
        ranges.append((cidr.version, cidr.last, cidr.first, cidr))

    ranges.sort()

    i = len(ranges) - 1
    while i > 0:
        if ranges[i][0] == ranges[i - 1][0] and \
                        ranges[i][2] <= ranges[i - 1][1] + N:
            version = ranges[i][0]
            new_last = max(ranges[i][1], ranges[i - 1][1])
            new_first = min(ranges[i][2], ranges[i - 1][2])
            ranges[i - 1] = (version, new_last, new_first)
            del ranges[i]
        i -= 1

    cidr_from_ranges = []

    for r in ranges:
        c = spanning_cidr([IPAddress(r[2]), IPAddress(r[1])])
        cidr_from_ranges.append(str(c))

    return cidr_from_ranges


# using csv to save tuple in this function was not good,, not easy to retrieve because of comma seperation
def gen_random_values_for_addr_types(d):
    global all_routes_util
    all_routes_util = dict()

    for asn, subnets in d.items():

        for subnet in subnets:
            util_key = asn + '_' + subnet
            size = IPNetwork(subnet).size
            # subnet with /32 subnet mask
            if size == 1:
                temp = ([size, 0, 1, 0])    # DHCP, Network, Critical
                all_routes_util[util_key] = temp
                continue
            # subnet with subnet mask /28
            if size <= 16:
                t2 = random.randint(0, int(size * 0.80))
                temp = ([size, 0, t2, 0])    # DHCP, Network, Critical
                all_routes_util[util_key] = temp
                continue

            t1 = random.randint(0, int(size * 0.50))
            t2 = random.randint(0, int(size * 0.20))
            t3 = random.randint(0, int(size * 0.05))

            temp = [size, t1, t2, t3]    # DHCP, Network, Critical
            # print temp
            if not util_key in all_routes_util:
                all_routes_util[util_key] = temp
    write_to_csv('/data/atreya/CS396A/src/media/all_routes_util.txt', all_routes_util)


def cost(s):
    if s not in all_routes_util:
        print('ERROR {} IS NOT IN all_routes_util'.format(s))
        return 1
    tmp = all_routes_util[s]
    t1 = math.ceil(int(tmp[1]) - 1 / int(tmp[0]))
    t2 = int(tmp[2]) - 1
    t3 = int(tmp[3]) - 1
    cost = t1 + TYPE_2_COST * t2 + TYPE_3_COST * t3
    return int(cost)


# cost function for each subnet
def cost_fuction(subnet):
    if subnet in all_routes_util:
        return cost(subnet)
    else:
        tmp = subnet.split('_')
        asn = tmp[0]
        c = 0
        subnets = supernet_subnets[subnet]
        for s in subnets:
            print(subnets, subnet)
            c = + cost(asn + '_' + s)
        return int(c)


def benefit_fuction(M, cs_size):
    benefit = M - cs_size
    return ALFA * benefit


def utility_function(overlapping, M, cs):
    total_cost = 0
    total_benefit = benefit_fuction(M, cs)
    for overlap in overlapping:

        total_cost += cost_fuction(overlap)

    return total_benefit - total_cost


def map_supernet_subnets(asn, supernet, merged):#, supernet_subnets_d):
    skey = asn + '_' + supernet
    if skey not in supernet_subnets:
        supernet_subnets[skey] = set()
        for m in merged:
            supernet_subnets[skey].add(str(m))
    else:
        for m in merged:
            supernet_subnets[skey].add(str(m))


def modify_supernet_subnets(asn, supernet, splitted_subnets):#, supernet_subnets_d):
    skey0 = asn + '_' + supernet
    skey1 = asn + '_' + splitted_subnets[0]
    skey2 = asn + '_' + splitted_subnets[1]

    supernet1 = IPNetwork(splitted_subnets[0])
    supernet2 = IPNetwork(splitted_subnets[1])

    subnets = supernet_subnets[skey0]

    if skey1 not in supernet_subnets:
        supernet_subnets[skey1] = set()

    if skey2 not in supernet_subnets:
        supernet_subnets[skey2] = set()

    for s in subnets:
        subnet = IPNetwork(s)
        if IPSet(subnet) & IPSet(supernet1):
            supernet_subnets[skey1].add(str(s))
        elif IPSet(subnet) & IPSet(supernet2):
            supernet_subnets[skey2].add(str(s))

    if len(supernet_subnets[skey1]) == 0:
        del supernet_subnets[skey1]
        splitted_subnets.pop(0)
    elif len(supernet_subnets[skey2]) == 0:
        del supernet_subnets[skey2]
        splitted_subnets.pop(1)

    del supernet_subnets[skey0]

    return splitted_subnets


def merge_split_process(d):
    global asn_supernets, supernet_subnets, M, N
    M = 0
    asn_supernets = d.copy()  # key = asn , value = list of summaries
    supernet_subnets = dict()  # key = asn_supernet, value = original list subnets
    N = 512
    M = routing_table_size(asn_supernets)
    W = []
    W.append((0, 0, N))  # (Welfare, Overlaps, N)
    cs_size = M
    welfare = 0

    # list of all locations (Each is identified with ASN #)
    ASNs = [n for n in asn_supernets.keys()]

    all_routes_sorted_list = dict_to_sorted_tuple(asn_supernets)

    # compute the summaries/supernets of subnets in each location
    overlapping_subnets = set()
    overlap_pairs = set()
    I = 0
    while I < 100:
        I += 1
        print ('_________________________________________________________________________________________________________')
        print ('*************************************  merging .... Iteration # {:0>2d} **************************************'\
            .format(I))

        for asn in ASNs:
            ip_addrs = asn_supernets[asn]

            subnets = []

            for ip in ip_addrs:
                cidr = IPNetwork(ip)
                subnets.append(cidr)

            subnets.sort()

            # print '# of subnets = {} in ASN {}\nSubnets :{}'.format(len(subnets), asn, subnets)

            i = len(subnets) - 1
            # going through list of subnets in one location
            while i >= 0:
                # do the merge of the last two in the list
                to_merge = [subnets[i], subnets[i - 1]]
                supernets = merge(to_merge, N)

                # if merge did not happen, same subnets will return ...
                # do nothing and continue to the next in the list
                if len(supernets) == 1:
                    # check whether the supernet overlaps any other subnet in other locations
                    new_overlap = str()
                    if is_overlapped(all_routes_sorted_list, asn, supernets[0]):
                        new_overlap = new_find_overlaps(all_routes_sorted_list, asn, supernets[0])
                        overlap_pair = (asn + '_' + supernets[0], new_overlap)
                        overlap_pairs.add(overlap_pair)
                        overlapping_subnets.add(new_overlap)

                    # evaluate welfare
                    cs_size -= 1
                    new_welfare = utility_function(overlapping_subnets, M, cs_size)
                    # if welfare increased add new supernet
                    if new_welfare > welfare:
                        subnets[i - 1] = IPNetwork(supernets[0])
                        subnets.pop(i)
                        welfare = new_welfare
                        # keep track of supernets and their subnets
                        map_supernet_subnets(asn, supernets[0], to_merge)#, supernet_subnets)
                        # if welfare did not increase, remove the added overlaps and reset the cs_size
                    else:
                        if new_overlap in overlapping_subnets:
                            overlapping_subnets.remove(new_overlap)
                        cs_size += 1
                    asn_supernets[asn] = subnets
                i -= 1
                # end of while loop

        print ('# of subnets before the merge process = {}\n' \
            '# of subnets after  the merge process = {}'.format(M, routing_table_size(asn_supernets)))
        print ('{} overlapped subnets, {} overlapped pairs, welfare {}, cs {}.'.format(len(overlapping_subnets),
                                                                                    len(overlap_pairs), welfare,
                                                                                    cs_size))
        print ('_________________________________________________________________________________________________________')
        print ('************************************* splitting .... Iteration # {:0>2d} *************************************' \
            .format(I))

        for asn in ASNs:
            ip_addrs = asn_supernets[asn]

            subnets = []

            for ip in ip_addrs:
                cidr = IPNetwork(ip)
                subnets.append(cidr)

            subnets.sort()

            i = len(subnets) - 1
            # going through list of subnets in one location
            while i >= 0:
                to_split = subnets[i]
                # add the asn to the subnet and put in to_split_asn
                to_split_asn = asn + '_' + str(to_split)
                if to_split_asn in overlapping_subnets:
                    cs_size += 1
                    overlapping_subnets.remove(to_split_asn)
                    new_welfare = utility_function(overlapping_subnets, M, cs_size)
                    tmp_splits = []
                    splits = []
                    if new_welfare > welfare:
                        prefix_len = to_split.prefixlen
                        if prefix_len < 32:
                            prefix_len += 1
                            tmp_splits = list(to_split.subnet(prefix_len))
                        splits = modify_supernet_subnets(asn, to_split, tmp_splits)#, supernet_subnets)
                        subnets.remove(to_split)
                        subnets.extend(splits)
                    else:
                        cs_size -= 1
                        overlapping_subnets.add(to_split_asn)

                    asn_supernets[asn] = subnets
                i -= 1
                # end of while loop

        print ('# of subnets before the merge process = {}\n' \
            '# of subnets after  the merge process = {}'.format(M, routing_table_size(asn_supernets)))
        print ('{} overlapped subnets, {} overlapped pairs, welfare {}, cs {}.'.format(len(overlapping_subnets),
                                                                                    len(overlap_pairs), welfare,
                                                                                    cs_size))
        print ('_________________________________________________________________________________________________________')

        print ('Total utility = {}'.format(welfare))#, W, W[len(W) - 1][0]
        if welfare == W[len(W) - 1][0]:
            break
        W.append((welfare, len(overlapping_subnets), N))

    return asn_supernets


# CHECK WHETHER OF NOT THERE IS AN OVERLAP WITH A SUBNET IN ANOTHER LOCATION
def is_overlapped(sorted_list_tuples, asn, subnet):
    first = 0
    last = len(sorted_list_tuples) - 1
    overlap = False
    item = IPNetwork(subnet)

    # start_binary_search = datetime.now()
    while first <= last and not overlap:
        midpoint = (first + last) // 2

        ip = sorted_list_tuples[midpoint][1]

        # print 'Is {} overlapping with {} ?'.format(item,ip)
        if IPSet(ip) & IPSet(item) and sorted_list_tuples[midpoint][0] != asn:
            overlap = True
        else:
            if item.first < ip.first:
                last = midpoint - 1
            else:
                first = midpoint + 1
    # print "--- start_binary_search {} seconds ---".format(datetime.now() - start_binary_search)
    return overlap


# SORT A ROUTING TABLE -- TAKE A DICTIONARY AND RETURNS A SORTED LIST OF TUPLES (ASN,SUBNET)
def dict_to_sorted_tuple(d):
    sorted_tuple = []
    for key, values in d.items():
        for value in values:
            ip = IPNetwork(value)
            sorted_tuple.append((key, ip))
        # SORT THE LIST OF TUPLES USING THE IP SUBNET
        sorted_tuple.sort(key=lambda tup: tup[1])

    return sorted_tuple


# RETURN THE OVERLAP WITH A SUBNET IN ANOTHER LOCATION
def new_find_overlaps(sorted_list_tuples, asn, subnet):
    first = 0
    last = len(sorted_list_tuples) - 1
    overlap = False
    item = IPNetwork(subnet)

    while first <= last and not overlap:
        midpoint = (first + last) // 2

        ip = sorted_list_tuples[midpoint][1]

        if IPSet(ip) & IPSet(item) and sorted_list_tuples[midpoint][0] != asn:
            return sorted_list_tuples[midpoint][0] + '_' + str(ip)
        else:
            if item.first < ip.first:
                last = midpoint - 1
            else:
                first = midpoint + 1

    return None


def create_conflict_graph(conflict_edges):
    # Create a graph
    G = nx.Graph()
    # add nodes and edges from the conflict list
    G.add_edges_from(conflict_edges)
    # update the nodes costs
    for v in G.nodes():
        print(v)
        cost = cost_fuction(v)
        G.nodes[v]['cost'] = cost
    return G


def routing_table_size(d):
    count = 0
    for k, v in d.items():
        for u in v:
            count += 1
    return count


def remove_subnets_to_be_changed(d, subnets):
    for i in subnets:
        temp = i.split('_')
        asn = temp[0]
        subnet = temp[1]
        removed = set()
        if subnet in d[asn] and subnet not in removed:
            d[asn].remove(subnet)
            removed.add(subnet)
            # print 'Successfully removed {} from {}'.format(subnet, asn)
        else:
            print ('Attempting to remove {} from {} and not found'.format(subnet, asn))

        if not d[asn]:
            # print 'asn {} has no subnets, {}'.format(asn, d[asn])
            del d[asn]
    return d


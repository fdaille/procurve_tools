# HP ProCurve Tools - CH Auban-Moët
# Copyright (c) 2022-2023
# Faustin DAILLÉ
import datetime, json, os, csv
from prettytable import PrettyTable
from tools import prettycsv, tableize, snmp_helper
import pandas as pd

# It creates the directories logs, switch and lti if they don't exist.
os.makedirs('files/logs', exist_ok=True)
os.makedirs('files/switch', exist_ok=True)
os.makedirs('files/lti', exist_ok=True)

# Defining the variables that are used in the script.
COMMUNITY = '' # A variable that is used to store the SNMP community name.
PATH = 'ressources\ip_list.txt' # Defining the path to the file that contains the IP addresses of the switches.
OUTPUTPATH = 'files'
OIDSPATH = 'ressources\OIDS.json' # Defining the path to the file that contains the OIDS.
LOGSPATH = r'files\logs'

# A list of HP Procurve switch models.
SW24 = ['J4903A','J9087A','J9299A','J9021A','J9625A','J8164A','J4900C']
SW48 = ['J9088A','J9022A','J9627A']
RT = ['J8698A','J8773A','J8697A','J4819A']

# Opening the file OIDS.json and assigning the values to the variables.
with open(f'{OIDSPATH}', 'r') as file:
    OIDS = json.load(file)
    oid_name = OIDS['system']['name']
    oid_model = OIDS['system']['model']
    oid_intype = OIDS['interfaces']['type']
    oid_indescr = OIDS['interfaces']['descr']
    oid_instatus = OIDS['interfaces']['status']
    oid_intincounter = OIDS['interfaces']['incounter']
    oid_intoutcounter = OIDS['interfaces']['outcounter']
    oid_vlanuntagged = OIDS['interfaces']['untagged']
    oid_errors = OIDS['interfaces']['errors']
    oid_drops = OIDS['interfaces']['drops']
    oid_speed = OIDS['interfaces']['speed']
    file.close



def getsnmp(ip, community, oid):
    """
    It takes an IP address, community string, and OID as input, and returns the value of the SNMP request
    as output
    """
    host = (ip, community, 161)
    request = snmp_helper.snmp_extract(snmp_helper.snmp_get_oid(host, oid, display_errors=True))
    return(request)


def ltiTableGen():
    """
    It creates a dataframe with the following columns:
    :return: A dataframe with the following columns:
    numLTI, nombreSW, intUP, intUSED
    """
    lti = []
    for i in range(1, 35):
        lti.append({
            "numLTI": str(i).zfill(2),
            "nombreSW": 0,
            "intUP": 0,
            "intUSED": 0
        })
    lti = pd.DataFrame.from_dict(lti)
    return lti


def main():
    # Opening file in read mode and assigning the file object to the variable `fichier`.
    with open(PATH, "r") as fichier:
        ltiTable = ltiTableGen() # Creating a dataframe
        # Creating a log file for the current day.
        time = str(datetime.datetime.now()).split(" ")
        logs = open(f"{LOGSPATH}\{time[0]}.log", "a")
        
        # A loop that iterates over the IP addresses in the file.
        for ip in fichier:
            # It removes the newline character from the IP address.
            ip = str(ip.replace("\n",""))
            try :
                # Getting the name and model of the switch.
                name = getsnmp(ip, COMMUNITY, oid_name)
                model = getsnmp(ip, COMMUNITY, oid_model)
                
                # Creating a table with the following columns: Interface, Status, Compteur, Erreurs,
                # Drops, Mode, VLAN Untagged.
                switchTable = PrettyTable(["Interface", "Status", "Compteur", "Erreurs", "Drops", "Mode","VLAN Untagged"])

                # Initializing the variables.
                interfaceNumber = 0
                upInt = 0
                countInt = 0

                # Checking if the model of the switch is in the list SW24 or SW48.
                if model in SW24 or model in SW48:
                    # Iterating over the range of interfaces number.
                    for i in range(1,52+1):
                        intType = getsnmp(ip, COMMUNITY, f'{oid_intype}.{i}') # Getting the type of the interface.

                        if intType == '6': # Checking if the interface type is ethernet.
                            # Getting the status of the interface and incrementing the upInt variable if the status is up.
                            interfaceNumber += 1
                            intStatus = getsnmp(ip, COMMUNITY, f'{oid_instatus}.{i}')
                            if intStatus == '1':
                                intStatus = 'up'
                                upInt += 1
                            else:
                                intStatus = 'down'
                            # Getting the number of bytes received and sent on the interface and adding them together.
                            intInCounter = int(getsnmp(ip, COMMUNITY, f'{oid_intincounter}.{i}'))
                            intOutCounter = int(getsnmp(ip, COMMUNITY, f'{oid_intoutcounter}.{i}'))
                            intCounter = intInCounter + intOutCounter

                            # Counting the number of interfaces that have a counter greater than 0.
                            if intCounter != 0:
                                countInt += 1

                            # Getting the errors, drops, speed and untagged vlan of the interface.
                            intErrors = getsnmp(ip, COMMUNITY, f'{oid_errors}.{i}')
                            intDrops = getsnmp(ip, COMMUNITY, f'{oid_drops}.{i}')
                            intSpeed = int(getsnmp(ip, COMMUNITY, f'{oid_speed}.{i}'))/10**6
                            intUntaggedVLAN = getsnmp(ip, COMMUNITY, f'{oid_vlanuntagged}.{i}')
                            # Adding a row to the table.
                            switchTable.add_row([i, intStatus, intCounter, intErrors, intDrops, intSpeed,intUntaggedVLAN])
                        else:
                            continue

                # Checking if the model of the switch is in the list RT.
                elif model in RT:
                    # Iterating over the range of interfaces number.
                    for i in range(1,289):
                        intType = getsnmp(ip, COMMUNITY, f'{oid_intype}.{i}') # Getting the type of the interface.
                        
                        if intType == '6': # Checking if the interface type is ethernet.
                            # Getting the status of the interface and incrementing the upInt variable if the status is up.
                            intDescr = getsnmp(ip, COMMUNITY, f'{oid_indescr}.{i}')
                            interfaceNumber += 1
                            intStatus = getsnmp(ip, COMMUNITY, f'{oid_instatus}.{i}')
                            if intStatus == '1':
                                intStatus = 'up'
                                upInt += 1
                            else:
                                intStatus = 'down' # Setting the status of the interface to down if the interface type is not ethernet.
                            
                            # Getting the number of bytes received and sent on the interface and adding them together.
                            intInCounter = int(getsnmp(ip, COMMUNITY, f'{oid_intincounter}.{i}'))
                            intOutCounter = int(getsnmp(ip, COMMUNITY, f'{oid_intoutcounter}.{i}'))
                            intCounter = intInCounter + intOutCounter

                            # Counting the number of interfaces that have a counter greater than 0.
                            if intCounter != 0:
                                countInt += 1

                            # Getting the errors, drops, speed and untagged vlan of the interface.
                            intErrors = getsnmp(ip, COMMUNITY, f'{oid_errors}.{i}')
                            intDrops = getsnmp(ip, COMMUNITY, f'{oid_drops}.{i}')
                            intSpeed = int(getsnmp(ip, COMMUNITY, f'{oid_speed}.{i}'))/10**6
                            intUntaggedVLAN = getsnmp(ip, COMMUNITY, f'{oid_vlanuntagged}.{i}')
                            # Checking if the untagged vlan is equal to "No Such Instance currently exists at this OID" and if it
                            # is, it is setting the untagged vlan to "Trk or null".
                            if intUntaggedVLAN == "No Such Instance currently exists at this OID":
                                intUntaggedVLAN = "Trk or null"
                            # Adding a row to the table.
                            switchTable.add_row([intDescr, intStatus, intCounter, intErrors, intDrops, intSpeed,intUntaggedVLAN])
                else:
                    continue

                # Adding the number of switches, the number of up interfaces and the number of used interfaces to the
                # LTI's dataframe.
                for i in range(1,35):
                    idx = str(i).zfill(2)
                    ltiN = f'{name[5]}{name[6]}'
                    if ltiN == idx:
                        ltiTable['nombreSW'][i-1] += 1
                        ltiTable['intUP'][i-1] += upInt
                        ltiTable['intUSED'][i-1] += countInt
                        break

                # Creating a string with the name, IP and model of the switch.
                head = f'+-------------------------------------------------+\n| Nom : {name}\n| IP : {ip}\n| Modèle : {model}\n'
                stats = f'+-------------------------------------------------+\n| Interfaces UP : {upInt}/{interfaceNumber}\n| Interfaces utilisées (compteur > 0) : {countInt}/{interfaceNumber}\n'
                
                # Creating a directory with the name of the switch and the date.
                repertoire = f'{OUTPUTPATH}\switch\SW_{time[0]}'
                os.makedirs(repertoire, exist_ok=True)

                # Writing the switchTable to a csv file.
                with open(f"{repertoire}\{name}_{time[0]}.csv", "w") as csvFile:
                    w = csv.writer(csvFile, delimiter =';')
                    w.writerows(prettycsv.prettycsv(str(switchTable)))
                    csvFile.close

                # Writing the head, stats and switchTable to a text file.
                with open(f"{repertoire}\{name}_{time[0]}.txt", "w") as textFile:
                    textFile.write(head + stats + str(switchTable))
                    textFile.close

                # Writing the date, time, name and IP of the switch to the log file and printing it to the console.
                log = f'{time[0]} {time[1]} : {name} - {ip} : Successful'
                logs.write(f'{log}\n')
                print(log)
            except:
                # Writing the date, time, IP and status of the switch to the log file and printing it to the console.
                log = f'{time[0]} {time[1]} : {ip} : Failed'
                logs.write(f'{log}\n')
                print(log)
                continue  

        # Creating a directory with the name of the switch and the date.
        ltiDir = f'{OUTPUTPATH}\lti\LTI_{time[0]}'
        os.makedirs(ltiDir, exist_ok=True)
        
        # Writing the ltiTable to a csv file and a text file.
        ltiTable.to_csv(f'{ltiDir}\LTI_{time[0]}.csv', sep=';', index=False)
        ltiTable = tableize.tableize(ltiTable)
        with open(f"{ltiDir}\LTI_{time[0]}.txt", "w") as ltiFile:
            ltiFile.write(str(ltiTable))

        # It closes the log file.
        logs.close


if __name__ == "__main__":
    main()
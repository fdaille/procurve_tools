# HP ProCurve Tools - CH Auban-Moët
# Copyright (c) 2022-2023
# Faustin DAILLÉ
import os
import tkinter
import pandas as pd
import prettytable
import tkinter
from tkinter import filedialog


def main():
    # Initializing the variables.
    up_int = 0
    used_int = 0
    swNum = 0
    bleu = 0
    violet = 0
    noir = 0
    vert = 0
    rouge = 0
    jaune = 0
    orange = 0
    gris = 0

    # Creating a list of vlans per colors.
    table_bleu = [82,83,84,85,86,87,88,201,202,203,204,205,206,207,208,100]
    table_violet = [2100,2101,2250,2251,2252,2521]
    table_noir = [50]
    table_vert = [6,7,89]
    table_rouge = [110]
    table_jaune = [70]
    table_orange = [1]
    table_gris = [5,10]

    # Creating a table with the headers Bleu, Violet, Noir, Vert, Rouge, Jaune, Orange, Gris, Ports
    # actifs, Ports utilisés, Nombre de switch/routeurs.
    vlanTable = prettytable.PrettyTable(["Bleu", "Violet", "Noir", "Vert", "Rouge", "Jaune", "Orange", "Gris", " Ports actifs", "Ports utilisés", "Nombre de switch/routeurs"])

    # Asking the user to select a directory.
    path = tkinter.filedialog.askdirectory (title = "Sélectionnez un répertoire de destination ...", mustexist = True)

    # Looping through all the files in the directory.
    for file in os.listdir(path):
        # Checking if the file extension is .csv.
        if 'csv' in file:
            swNum += 1 # Incrementing the variable swNum by 1.
            df = pd.read_csv(f'{path}/{file}', sep=';') # Reading the csv file and storing it in a dataframe.
            # Looping through the rows of the dataframe.
            for i in range(0, df.shape[0]):
                # Checking if the status of the port is up and if it is, it increments the variable
                # up_int by 1.
                if df['Status'][i] == 'up':
                    up_int += 1
                # Checking if the value of the column Compteur is not equal to 0. If it is not equal
                # to 0, it increments the variable used_int by 1.
                if df['Compteur'][i] != 0:
                    used_int += 1
                    vlan = df['VLAN Untagged'][i] # Getting the value of the column VLAN Untagged at the index i.
                    # Checks if the value of the vlan variable is in one of the lists, if it is, it increments the
                    # variable of the list by 1.
                    if vlan in table_bleu:
                        bleu += 1
                    if vlan in table_violet:
                        violet += 1
                    if vlan in table_noir:
                        noir += 1
                    if vlan in table_vert:
                        vert += 1
                    if vlan in table_rouge:
                        rouge += 1
                    if vlan in table_jaune:
                        jaune += 1
                    if vlan in table_orange:
                        orange += 1
                    if vlan in table_gris:
                        gris += 1
    # Adding a row to the table.
    vlanTable.add_row([bleu,violet,noir,vert,rouge,jaune,orange,gris,up_int,used_int, swNum])

    # Asking the user to select a directory and then saving the table in a text file.
    file = filedialog.asksaveasfile(initialdir=f'{os.environ["USERPROFILE"]}\Desktop', initialfile='cables.txt',filetypes=(("Text Files", "*.txt"),
                                       ("All files", "*.*") ))
    file.write(str(vlanTable))


if __name__ == "__main__":
    main()
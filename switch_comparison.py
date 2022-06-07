# HP ProCurve Tools - CH Auban-Moët
# Copyright (c) 2022-2023
# Faustin DAILLÉ
import webbrowser
import pandas as pd
from tools import tableize
from tkinter import filedialog
from guizero import *


def compare(swName, oldFile, newFile):
    # Reading the csv files and assigning them to variables.
    data1 = pd.read_csv(oldFile, sep=";")
    data2 = pd.read_csv(newFile, sep=";")

    # Creating a dataframe with the columns listed.
    df = pd.DataFrame(columns=['Interface', 'Status', 'Compteur', 'Erreurs', 'Drops', 'VLAN Untagged'])

    # Looping through the rows of the dataframe and calculating the difference between the two dataframes.
    for i in range(0, data1.shape[0]):
        changes_counter = data2['Compteur'][i] - data1['Compteur'][i]
        changes_errors = data2['Erreurs'][i] - data1['Erreurs'][i]
        changes_drops = data2['Drops'][i] - data1['Drops'][i]

        # Adding a plus sign to the front of the number if it is greater than 0.
        if changes_counter > 0:
            changes_counter = f'+{changes_counter}'
        if changes_errors > 0:
            changes_errors = f'+{changes_errors}'
        if changes_drops > 0:
            changes_drops = f'+{changes_drops}'


        # Adding a row to the dataframe.
        df.loc[i] = [data2['Interface'][i], data2['Status'][i], changes_counter, changes_errors, changes_drops, data2['VLAN Untagged'][i]]

    # Creating a string with the name of the switch and the table.
    head = f'+-------------------------------------------------+\n| Nom : {swName}\n'
    content = tableize.tableize(df)

    # Saving the file to the desktop.
    fname = filedialog.asksaveasfile(initialdir=f'{os.environ["USERPROFILE"]}\Desktop', initialfile=f'{swName}.txt',filetypes=(("Text Files", "*.txt"),
                                       ("All files", "*.*") ))
    fname.write(head + str(content))

def menubar_exit():
    """
    It destroys the app.
    """
    app.destroy()

def menubar_doc():
    """
    It opens the documentation in the default browser
    """
    webbrowser.open('https://docs.faustin-daille.fr/books/procurve-tools')

def path1():
    """
    It opens a file dialog box and returns the file path of the selected file.
    """
    folder_path1 = filedialog.askopenfilename()
    file_name = str(folder_path1).split("/")[-1]
    input_box0.value = file_name.split("_")[0]
    input_box1.value = folder_path1

def path2():
    """
    It opens a file dialog box and returns the path of the file selected by the user.
    """
    folder_path2 = filedialog.askopenfilename()
    input_box2.value = folder_path2

def compare_files():
    """
    If the first input box is empty, display a message in the first output box.
    If the second input box is empty, display a message in the second output box.
    If both input boxes are not empty, run the comparer function.
    """
    if input_box1.value == '':
        message1.value = "\nChoissisez un fichier plus ancien : * Obligatoire"
    if input_box2.value == '':
        message2.value = "\nChoissisez un fichier plus récent : * Obligatoire"
    else:
        compare(input_box0.value, input_box1.value, input_box2.value)


# It creates a window with the title "Switch COMPARISON" and the dimensions 475x800.
app = App(title="Switch COMPARISON", height=475, width=800)

# Creating a picture object and assigning it to the variable `picture`.
picture = Picture(app, image="ressources/img/logo.png")

# It creates a menu bar with two options: File and Help.
menubar = MenuBar(app,
                toplevel=["File", "Help"],
                options=[
                    [ ["Exit", menubar_exit] ],
                    [ ["Documentation", menubar_doc] ]
                ])


# It creates a text object and assigns it to the variable `message0`.
# It creates a text box object and assigns it to the variable `input_box0`.
message0 = Text(app, text="\nNom de l'équipement :")
input_box0 = TextBox(app, width=30, enabled=False)

# It creates a text object and assigns it to the variable `message1`.
# It creates a text box object and assigns it to the variable `input_box1`.
# It creates a button object and assigns it to the variable `button1`.
message1 = Text(app, text="\nChoissisez un fichier plus ancien :")
input_box1 = TextBox(app, width=50)
button1 = PushButton(app, text="Parcourir", command=path1) # Appel la fonction "path1"

# It creates a text object and assigns it to the variable `message2`.
# It creates a text box object and assigns it to the variable `input_box2`.
# It creates a button object and assigns it to the variable `button2`.
message2 = Text(app, text="\nChoissisez un fichier plus récent :")
input_box2 = TextBox(app, width=50)
button2 = PushButton(app, text="Parcourir", command=path2)

# It creates a button object and assigns it to the variable `button3`.
button3 = PushButton(app, text="Valider", command=compare_files, align="right")

# It displays the window.
app.display()
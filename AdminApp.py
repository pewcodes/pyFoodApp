import sqlite3
import os
import tkinter as tk
import tkinter.ttk as ttk
from PIL import ImageTk, Image
import io
from tkinter import StringVar, messagebox, Menu, filedialog

fileName = "foodList.txt"
fileNameDB = "foodList.db"
g_img = []

class FoodItemName:
    def __init__(self,name,image):
        self.__name=name
        self.__image=image
    def getName(self):
        return self.__name
    def getImage(self):
        return self.__image
    
def loadData(fileName):                                                     # Load data from text file to create sqlite database file
    file = open(fileName,"r")
    lines = file.readlines()
    conn = sqlite3.connect(fileNameDB)
    sql = "create table FoodData(Name text primary key,Category text,Description text,Price float,ImageLink text)"
    conn.execute(sql)
    for line in lines:
        line = line.replace("\n","")
        cols = line.split("|")
        name = cols[0]
        category = cols[1]
        description = cols[2]
        price = float(cols[3])
        sql = "insert into FoodData(Name,Category,Description,Price) values(?,?,?,?)"
        conn.execute(sql,(name,category,description,price))
    conn.commit()
    conn.close()
    file.close()

#----- Treeview -----#
def TData():
    for i in tree.get_children():                                           # Clear all items in the treeview
        tree.delete(i)
    conn = sqlite3.connect(fileNameDB)
    cur = conn.cursor()
    cur.execute("SELECT * FROM FoodData")
    row = cur.fetchone()
    i=0
    while row is not None:
        name=row[0]
        img=row[4]
        if img is not None:
            tree.insert("",i,text=name,values=img,iid=str(i))
        else:
            tree.insert("",i,text=name,iid=str(i))
        i+=1
        row = cur.fetchone()
    conn.close()                                                            # Bind iid with List item index
		
def refreshTData():
    clearTextBoxes()                                                        # Loads treeview data
    TData()
    messagebox.showinfo("Success","Data Refreshed!")

def selectItem(e):                                                          # Obtains selection name, simplifies deletion/update func
    clearTextBoxes()
    try: 
        curItem = tree.selection()                                           
        iid = curItem[0]
        txtName.set(tree.item(iid)["text"])
        if tree.item(iid)["values"] != "":
            try:                                                            # Load image if available
                path = tree.item(iid)["values"][0]
                img = Image.open(path).resize((150, 150), Image.ANTIALIAS)
                g_img.append(ImageTk.PhotoImage(img))
                cv.create_image(80,80, image=g_img[-1])
            except:                                                         # Else, loads "NP.jpg"
                img = Image.open("img/NP.jpg").resize((150, 150), Image.ANTIALIAS)
                g_img.append(ImageTk.PhotoImage(img))
                cv.create_image(80,80, image=g_img[-1])    
    except IndexError:                                                      # Accept error when admin selects empty treeview
        pass                                 
        
#----- Manage Data with Buttons -----#
def addData():                                                              # Insert new food item to database
    conn = sqlite3.connect(fileNameDB)
    name = txtName.get()
    category = txtCategory.get()
    description = txtDescription.get()
    price = txtPrice.get()
    image = txtImage.get()
    namelist = []
    for c in tree.get_children(): 
        namelist.append(tree.item(c)["text"])  
    if name not in namelist:                                                # Check for existing data in appended namelist
        if name and category and description and price and image != "":     # Ensure no empty fields for adding
            if checkFloat(price) == True:                                   # Check if price entered is numeric
                sql = "insert into FoodData(Name,Category,Description,Price,ImageLink) values(?,?,?,?,?)"
                conn.execute(sql,(name,category,description,price,image))
            else:
                return
        else:
            messagebox.showerror("Error","Please input all data fields for adding.")
            return
    else:                                                                   # If item already exists, shows error
        tk.messagebox.showerror("Error","Item Exists.")
        return
    conn.commit()
    conn.close()
    clearTextBoxes()
    TData()
    messagebox.showinfo("Success","Insert Successful!")

def updateData():
    conn = sqlite3.connect(fileNameDB)
    c = conn.cursor()
    category = txtCategory.get()                                            # Get all inputs data
    description = txtDescription.get()
    price = txtPrice.get()
    image = txtImage.get()
    name = txtName.get()
    c.execute("SELECT Name FROM FoodData")                                  # Select only field "Name" from database
    names = {name[0] for name in c.fetchall()}                              # Build set with names as [('name1',), ('name2',)]
    if name != "":                                                          # Ensure Primary Key - "Name" is not empty
        if name in names:                                                   # Ensure name exists in Database for updates to proceed
            if category or description or price or image != "":             # Ensure no empty fields for updating
                if category != "":
                    sql = "UPDATE FoodData SET Category = ? WHERE Name = ?"
                    conn.execute(sql,(category,name))
                if description != "":
                    sql = "UPDATE FoodData SET Description = ? WHERE Name = ?"
                    conn.execute(sql,(description,name))
                if price != "":
                    if checkFloat(price) == True:
                        sql = "UPDATE FoodData SET Price = ? WHERE Name = ?"
                        conn.execute(sql,(price,name))
                    else:
                        return
                if image != "":
                    sql = "UPDATE FoodData SET ImageLink = ? WHERE Name = ?"
                    conn.execute(sql,(image,name))
            else:                                                           # If no data inputs shows error
                messagebox.showerror("Error","Please input data for update.")
                return
        else:                                                               # If not existing "Name" shows error
            messagebox.showerror("Error","Please input an existing food item for update.")
            return
    else:                                                                   # If empty field at "Name" shows error
        messagebox.showerror("Error","Please input Name of food item.")
        return
    conn.commit()
    conn.close()
    clearTextBoxes()
    TData()                                                    
    messagebox.showinfo("Success","Update Successful!")

def deleteData():                                                           # Delete food item from database
    conn=sqlite3.connect(fileNameDB)
    c = conn.cursor()
    name=txtName.get()
    c.execute("SELECT Name FROM FoodData")                                  
    names = {name[0] for name in c.fetchall()}                              
    if name != "":                                                          # Ensure Primary Key "Name" is not empty
        if name in names: 
            sql="delete from FoodData where Name = ?"
            conn.execute(sql,(name,))                                       # Extra comma for single value
        else:                                                               # If not existing "Name" shows error
            messagebox.showerror("Error","Please input an existing food item for deletion.")
            return
    else:                                                                   # If empty field at "Name" shows error
        messagebox.showerror("Error","Please input Name of food item for deletion.")
        return                              
    conn.commit()
    conn.close()
    clearTextBoxes()
    TData()
    messagebox.showinfo("Success","Delete Successful!")

def clearTextBoxes():                                                       # Clear text in textboxes                                 
    txtName.set("")
    txtCategory.set("")
    txtDescription.set("")
    txtPrice.set("")
    txtImage.set("")
    defaultImage()                                                          # Initialize preview image

#----- Manage Preview Image -----#
def previewImage():                                                         # After inputting imagelink
    global g_img
    global cv
    path = txtImage.get()
    if path != "":
        img = Image.open(path).resize((150, 150), Image.ANTIALIAS)
        g_img.append(ImageTk.PhotoImage(img))  
        cv.create_image(80,80, image=g_img[-1])
    else:                                                                   # If empty field at "Image Link" shows error
        messagebox.showerror("Error","Please input Image Link.")
        return

def defaultImage():
    global g_img
    global cv
    img = Image.open("img/NP.jpg").resize((150, 150), Image.ANTIALIAS)
    g_img.append(ImageTk.PhotoImage(img))
    cv.create_image(80,80, image=g_img[-1])

def browseFile():
    pathFile = filedialog.askopenfilename(initialdir = "img/",title = "Select file",filetypes = (("jpeg files","*.jpg"),("all files","*.*")))
    pathImage = os.path.join(os.path.basename(os.path.dirname(pathFile)), os.path.basename(pathFile))  # Joins both path and filename to get "img/name.jpg"
    txtImage.set(pathImage)                                                 # Set the path to the "Image Link" entry
    defaultImage()                                                          # Clear any previous preview image

#----- Other App Functions -----#
def initMsg(window, message):                                               # Window pop-up upon App launch
    tk.messagebox.showinfo("Food Admin", message)

def quitDialog():                                                           # Window pop-up to confirm exiting App
    dialogTitle = "Food Admin - Confirmation"
    dialogText = "Are you sure you want to 'Quit'?"
    ans = messagebox.askquestion(dialogTitle, dialogText)
    if ans == "yes":
        window.destroy()
    else:
        messagebox.showinfo("Food Admin - Confirmation","You must have clicked the wrong button accidentally.")

def about():
    aboutWindow = tk.Toplevel(window)
    aboutWindow.title("About App")
    aboutWindow.geometry("300x400")
    aboutWindow.resizable(0,0)
    #----- Tabs Creation -----#
    tabs = ttk.Notebook(aboutWindow)
    tab1 = ttk.Frame(tabs, width=280, height=280)
    tab2 = ttk.Frame(tabs, width=280, height=280)
    tabs.grid(row=1,rowspan=10,column=3,sticky="nsew")
    #----- Read txt files -----#
    file = open("abtMisc.txt","r")
    abtMisc = file.read()
    file.close()
    file = open("abtAdmin.txt","r")
    abtAdmin = file.read()
    file.close()
    file = open("abtUser.txt","r")
    abtUser = file.read()
    file.close()
    #----- Tab 1 -----#
    tabs.add(tab1, text="Admin")
    textTab1 = tk.Text(tab1, height=26, width=34, wrap="word")
    textTab1.grid(row=0, column=0, sticky="ew")
    aboutText1 = "\n" + abtAdmin + "\n\n" + abtMisc                         # Input info texts to "About" - Admin Tab
    textTab1.delete(1.0, tk.END)
    textTab1.insert(tk.END, aboutText1)
    ttk.Separator(tab1, orient=tk.HORIZONTAL).place(x=3, y=31, relwidth=0.96)
    ttk.Separator(tab1, orient=tk.HORIZONTAL).place(x=3, y=252, relwidth=0.96)
    textTab1.config(font=("Courier", 12))
    textTab1.config(state=tk.DISABLED)
    #----- Tab 2 -----#
    tabs.add(tab2, text="User")
    textTab2 = tk.Text(tab2, height=26, width=34, wrap="word")
    textTab2.grid(row=0, column=0, sticky="ew")
    aboutText2 = "\n" + abtUser + "\n\n" + abtMisc                          # Input info texts to "About" - User Tab
    textTab2.delete(1.0, tk.END)
    textTab2.insert(tk.END, aboutText2)
    ttk.Separator(tab2, orient=tk.HORIZONTAL).place(x=3, y=31, relwidth=0.96)
    ttk.Separator(tab2, orient=tk.HORIZONTAL).place(x=3, y=148, relwidth=0.96)
    textTab2.config(font=("Courier", 12))
    textTab2.config(state=tk.DISABLED)

def credit():
    creditsWindow = tk.Toplevel(window)
    creditsWindow.title("Credits")
    creditsWindow.geometry("300x250")
    creditsWindow.resizable(0,0)
    file = open("credits.txt","r")
    creditsText = file.read()
    file.close()
    textCredits = tk.Text(creditsWindow, height=26, width=34, wrap="word")
    textCredits.grid(row=0, column=0, sticky="ew")
    textCredits.delete(1.0, tk.END)
    textCredits.insert(tk.END, creditsText)
    textCredits.config(font=("Courier", 12), state=tk.DISABLED)
    ttk.Separator(creditsWindow, orient=tk.HORIZONTAL).place(x=3, y=16, relwidth=0.98)
    ttk.Separator(creditsWindow, orient=tk.HORIZONTAL).place(x=3, y=43, relwidth=0.98)
    ttk.Separator(creditsWindow, orient=tk.HORIZONTAL).place(x=3, y=159, relwidth=0.98)

#----- Numeric Validation -----#
def checkFloat(adminInput):                                                 # Test adminInput, accept floats only
    try:
        float(adminInput)
        return True
    except ValueError:
        tk.messagebox.showerror("Error","Please enter an numerical value for Price.")
        return False
    
if not os.path.exists("foodList.db"):                                       # Load text file data and get the list of food
    loadData(fileName)


#----- Main GUI	-----#
window = tk.Tk() 
window.title("Food Admin")
window.geometry("450x450")                                                  # Declare size of the app
window.resizable(0, 0)                                                      # Disable resizing in x or y direction

menuBar = Menu(window)                                                      # Create main menu bar
fileMenu = Menu(menuBar, tearoff=0)                                         # Create submenu (tearoff: if menu can pop-out)                                                     
menuBar.add_cascade(label="File", menu=fileMenu)                            # Add "File" dropdown sub-menu in main menu bar
fileMenu.add_command(label="Quit", command=quitDialog)                      # Add commands in submenu
helpMenu = Menu(menuBar, tearoff=0)
menuBar.add_cascade(label="Help", menu=helpMenu)
helpMenu.add_command(label="About Food App", command=about)
fileMenu.add_separator()
helpMenu.add_command(label="Credits", command=credit)
window.config(menu=menuBar)

labelAppName = ttk.Label(window,text="FOOD ADMIN",padding=2)
labelAppName.config(font=("Courier", 20, "bold"))
labelAppName.grid(row=0,column=0,columnspan=4,padx=(10,0),pady=10,sticky="ew")

#----- Texts & Entry Fields -----#
labelName = ttk.Label(window,text="Name")
labelName.config(font=("Courier", 14))
labelName.grid(row=1,column=1,sticky="w",padx=(10,5))
txtName = StringVar()
entry1 = ttk.Entry(window,textvariable=txtName)
entry1.grid(row=1,column=2)

labelCat = ttk.Label(window,text="Category")
labelCat.config(font=("Courier", 14))
labelCat.grid(row=2,column=1,sticky="w",padx=(10,5))
txtCategory = StringVar()
entry2 = ttk.Entry(window,textvariable=txtCategory)
entry2.grid(row=2,column=2)

labelDesc = ttk.Label(window,text="Description")
labelDesc.config(font=("Courier", 14))
labelDesc.grid(row=3,column=1,sticky="w",padx=(10,5))
txtDescription = StringVar()
entry3 = ttk.Entry(window,textvariable=txtDescription)
entry3.grid(row=3,column=2)

labelPrice = ttk.Label(window,text="Price")
labelPrice.config(font=("Courier", 14))
labelPrice.grid(row=4,column=1,sticky="w",padx=(10,5))
txtPrice = StringVar()
entry4 = ttk.Entry(window,textvariable=txtPrice)
entry4.grid(row=4,column=2)

#----- Image File Selection, Preview ----#
labelImage = ttk.Label(window,text="Image Link")
labelImage.config(font=("Courier", 14))
labelImage.grid(row=5,column=1,sticky="w",padx=(10,5))
txtImage = StringVar()
entry5 = ttk.Entry(window,textvariable=txtImage,width=15)
entry5.grid(row=5,column=2,sticky="w")

browsebutton = ttk.Button(window,text="...",command=browseFile,width=1)
browsebutton.place(x=277,y=165,anchor="e")

cv = tk.Canvas(window,height=150,width=150)                                 # Create image canvas
cv.place(x=440,y=25,anchor="ne")
defaultImage()                                                              # Initialize preview image

bPreview = ttk.Button(window,text="Preview Image",command=previewImage)     # "Preview Image" button
bPreview.place(relx=0.94,rely=0.44,anchor="e")

#----- Treeview -----#
tree = ttk.Treeview(window)
tree.heading("#0",text="Food Database")
style = ttk.Style(window)
style.configure('Treeview', rowheight=15)
tree.grid(row=8,column=0,columnspan=3,padx=(10,0),pady=10,sticky="nsew")
TData()
tree.bind('<ButtonRelease-1>', selectItem)

#----- Refresh, Add, Delete, Update Data Buttons -----#
bRefresh = ttk.Button(window,text='Refresh Database',command=refreshTData)  # "Refresh" data button
bRefresh.place(relx=0.79,rely=0.85,anchor="c")

bInsert = ttk.Button(window,text='Add',command=addData)                     # "Add" data button
bInsert.place(relx=0.12,rely=0.85,anchor="c")

bDelete = ttk.Button(window,text='Delete',command=deleteData)               # "Delete" data dutton
bDelete.place(relx=0.32,rely=0.85,anchor="c")

bUpdate = ttk.Button(window,text='Update',command=updateData)               # "Update" data Button
bUpdate.place(relx=0.52,rely=0.85,anchor="c")

#----- Credits -----#
creditMsg = tk.Message(window, text='By| Pewcodes')
creditMsg.config(font=("Courier", 8))
creditMsg.place(relx=0.98,rely=0.98,anchor="se")

window.after_idle(initMsg, window, "Admin App Initialize!")
window.mainloop()                                                           # Main loop to wait for events

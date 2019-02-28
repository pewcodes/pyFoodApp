import sqlite3
import os
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import StringVar, messagebox, Menu
from PIL import ImageTk, Image
import math

class FoodItem:
    def __init__(self,name,category,description,price,image):
        self.__name=name
        self.__category=category
        self.__description=description
        self.__price=price
        self.__image=image
    def getName(self):
        return self.__name
    def setName(self,name):
        self.__name=name
    def getCategory(self):
        return self.__category
    def setCategory(self,category):
        self.__category=category
    def getDescription(self):
        return self.__description
    def setDescription(self,description):
        self.__description=description
    def getPrice(self):
        return self.__price
    def setPrice(self,price):
        self.__price=price
    def getPriceWithGST(self):
        return("{:.2f}".format(self.__price*1.07))
    def getImage(self):
        return self.__image

fileName="foodList.db"                                                          # Loading data from sqlite database file
listOfFoodItems=[]
g_img=[]

def loadData(fileName):
    foodList = []
    foodLists = []
    conn = sqlite3.connect(fileName)
    cur = conn.cursor()
    cur.execute("SELECT * FROM FoodData")
    row = cur.fetchone()
    while row is not None:
        name = row[0]
        category = row[1]
        description = row[2]
        price = row[3]
        image = row[4]
        foodList = FoodItem(name,category,description,price,image)
        foodLists.append(foodList)
        row = cur.fetchone()
    conn.close()
    return foodLists

def reloadData():                                                               # Reload data and informs user
	global listOfFoodItems
	listOfFoodItems = loadData(fileName)
	updateTreeView()
	messagebox.showinfo("Data Load","Data Loaded!")

def updateTreeView():                                                           # Update Tree View of Food info
	for i in tree1.get_children():                                              # Clear all items in the tree view
		tree1.delete(i)
	i=0
	for food in listOfFoodItems:                                                # Bind iid with List item index
		tree1.insert("",i,text=food.getName(),iid=str(i))   
		i+=1
	clearTextBoxes()

def selectItem(e):
    clearTextBoxes()
    curItem = tree1.selection()                                                 # Get the iid 
    iid=int(curItem[0])
    try:
        loadImage(listOfFoodItems[iid].getImage())
    except:
        loadImage("img/NP.jpg")
    txtCategory.set(listOfFoodItems[iid].getCategory())
    txtPrice.set("$"+str(listOfFoodItems[iid].getPriceWithGST()))
    textDescription.config(state=tk.NORMAL)
    textDescription.delete(1.0, tk.END)
    textDescription.insert(tk.END,listOfFoodItems[iid].getDescription())
    textDescription.config(state=tk.DISABLED)

#----- Filters & Searches -----#
def filterFood():                                                               # Filter matching food name
	for i in tree1.get_children():                                              # Clear treeview items
		tree1.delete(i)
	i=0
	searchStr = txtSearch.get().upper()
	for food in listOfFoodItems:
		if food.getName().upper().find(searchStr)>-1:                       
			tree1.insert("",i,text=food.getName(),iid=str(i))                   # Bind the iid with the List item index
		i+=1

def filterCategory():
    i=0     
    searchStr = txtSearch.get().upper()                                         # Filter matching category
    for cat in listOfFoodItems:
        if cat.getCategory().upper().find(searchStr)>-1:
            for c in tree1.get_children():                                      # Delete duplicates for searches
                if int(i) == int(c):
                    tree1.delete(c)
            tree1.insert("",i,text=cat.getName(),iid=str(i))
        i+=1

def searches():                                                                 # Perform searches that filters name & category
    scaleVar.set(0)
    txtCategory.set("")
    txtPrice.set("")
    defaultImage()
    textDescription.config(state=tk.NORMAL)
    textDescription.delete(1.0, tk.END)
    textDescription.config(state=tk.DISABLED)
    filterFood()
    filterCategory()
    if len(tree1.get_children()) == 0:
        messagebox.showinfo("Search Result","No results found.")

def highestPrice():                                                             # Determine the highestPrice for Scale's maxrange
    conn = sqlite3.connect(fileName)
    c = conn.cursor()
    c.execute("SELECT Price FROM FoodData")
    prices = [price[0] for price in c.fetchall()]
    prices.sort()
    highP = prices[len(prices)-1] * 1.07
    conn.close()
    return math.ceil(highP)

def initScale(e):
    clearTextBoxes()

def filterPrice():
    clearTextBoxes()
    for i in tree1.get_children():                                              # Clear treeview items
        tree1.delete(i)
    i=0                                                                         # Search and filter matching category
    for i in range(len(listOfFoodItems)):                                       # Checking price based on floats
        if float(listOfFoodItems[i].getPriceWithGST()) <= float(scaleVar.get()):     
            tree1.insert("",i,text=listOfFoodItems[i].getName(),iid=str(i))
        i+=1

def clearTextBoxes():                                                           # Clear texts in textboxes 
    txtSearch.set("")                                                    
    txtCategory.set("")
    txtPrice.set("")
    defaultImage()
    textDescription.config(state=tk.NORMAL)
    textDescription.delete(1.0, tk.END)
    textDescription.config(state=tk.DISABLED)

#----- Manage Preview Image -----#
def loadImage(path):                                                            # Preview image after inputting imagelink
    global g_img
    global cv
    try:
        img = Image.open(path).resize((150, 150), Image.ANTIALIAS)
        g_img.append(ImageTk.PhotoImage(img)) 
        cv.create_image(80,80, image=g_img[-1])
    except:
        img = Image.open("img/NP.jpg").resize((150, 150), Image.ANTIALIAS)
        g_img.append(ImageTk.PhotoImage(img)) 
        cv.create_image(80,80, image=g_img[-1])

def defaultImage():                                                             # Initialize preview image
    global g_img
    global cv
    img = Image.open("img/NP.jpg").resize((150, 150), Image.ANTIALIAS)
    g_img.append(ImageTk.PhotoImage(img))
    cv.create_image(80,80, image=g_img[-1])

#----- Other App Functions -----#
def quitDialog():
    dialogTitle = "Food App - Confirmation"
    dialogText = "Are you sure you want to 'Quit'?"
    ans = messagebox.askquestion(dialogTitle, dialogText)
    if ans == "yes":
        window.destroy()
    else:
        messagebox.showinfo("Food App - Confirmation","You must have clicked the wrong button accidentally.")

def initMsg(window, message):                                                   # Window pop-up upon App launch
    tk.messagebox.showinfo("Food App", message)

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
    #----- Read .txt files-----#
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
    abtText1 = "\n" + abtAdmin + "\n\n" + abtMisc                               # Input info texts to "About" - Admin Tab
    textTab1.delete(1.0, tk.END)
    textTab1.insert(tk.END, abtText1)
    ttk.Separator(tab1, orient=tk.HORIZONTAL).place(x=3, y=31, relwidth=0.96)
    ttk.Separator(tab1, orient=tk.HORIZONTAL).place(x=3, y=252, relwidth=0.96)
    textTab1.config(font=("Courier", 12))
    textTab1.config(state=tk.DISABLED)
    #----- Tab 2 -----#
    tabs.add(tab2, text="User")
    textTab2 = tk.Text(tab2, height=26, width=34, wrap="word")
    textTab2.grid(row=0, column=0, sticky="ew")
    abtText2 = "\n" + abtUser + "\n\n" + abtMisc                                # Input info texts to "About" - User Tab
    textTab2.delete(1.0, tk.END)
    textTab2.insert(tk.END, abtText2)
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


#----- Main GUI -----#	
window = tk.Tk() 
window.title("Food App")
window.geometry("350x700")                                                      # Size of app window
window.resizable(0, 0)                                                          # Disable resizing in x or y direction

#----- MenuBar -----#
menuBar = Menu(window)                                                          
fileMenu = Menu(menuBar, tearoff=0)                                             # Create submenu (tearoff: if menu can pop-out)                                                     
menuBar.add_cascade(label="File", menu=fileMenu)                                # Add "File" dropdown sub-menu in main menu bar
fileMenu.add_command(label="Quit", command=quitDialog)                          # Add commands in submenu
helpMenu = Menu(menuBar, tearoff=0)
menuBar.add_cascade(label="Help", menu=helpMenu)
helpMenu.add_command(label="About Food App", command=about)
fileMenu.add_separator()
helpMenu.add_command(label="Credits", command=credit)
window.config(menu=menuBar)

labelAppName = ttk.Label(window,text="FOOD MENU",padding=2)
labelAppName.config(font=("Courier", 20, "bold"))
labelAppName.grid(row=0,column=0,columnspan=4,pady=10)

#----- Text Fields -----#
txtSearch = StringVar()
entry1 = ttk.Entry(window,textvariable=txtSearch)
entry1.grid(row=1,column=0,columnspan=2,padx=(10,0),sticky='NSEW')
bSearch = ttk.Button(window,text='Search',command=searches)                     # Search food button
bSearch.grid(row=1,column=2)

#----- Scale for Price Filtering -----#
scaleVar = tk.IntVar()
scaleVar.set(0)
wScale = ttk.Label(window,text="Max Price $",padding=2)
wScale.grid(row=2,column=0,padx=(10,0),pady=2)
wScale = tk.Scale(window,from_=0,to=highestPrice(),variable=scaleVar,orient="horizontal")
wScale.grid(row=2,column=1,columnspan=1,padx=2,pady=(0,15),sticky='NSEW')
wScale.bind('<ButtonRelease-1>', initScale)
bScale = ttk.Button(window,text='Filter',command=filterPrice)                   # Filter price button
bScale.grid(row=2,column=2)

#----- Canvas for Image Preview -----#
cv = tk.Canvas(window,height=150,width=150)
cv.grid(row=3,column=0,columnspan=2,padx=(8,0),pady=(0,5),sticky='NW')
defaultImage()

#----- Labels -----#
labelDescription = ttk.Label(window,text="Description",padding=2)
labelDescription.place(relx=0.5,rely=0.19,anchor="nw")
textDescription = tk.Text(height=9,width=22,wrap=tk.WORD)
textDescription.config(bg="gray99",font=("Courier",12))
textDescription.place(relx=0.49,rely=0.31,anchor="w")
textDescription.config(state=tk.DISABLED)

labelCategory = ttk.Label(window,text="Category",padding=2)
labelCategory.grid(row=5,column=0,sticky=tk.W,padx=(10,0))
txtCategory = StringVar()
textCategory = ttk.Entry(window,textvariable=txtCategory,state='readonly')
textCategory.grid(row=5,column=1,pady=2)

labelPrice = ttk.Label(window,text="Price(GST)",padding=2)
labelPrice.grid(row=7,column=0,sticky=tk.W,padx=(10,0))
txtPrice = StringVar()
textPrice = ttk.Entry(window,textvariable=txtPrice,state='readonly')
textPrice.grid(row=7,column=1,pady=2)

#----- Database & Treeview -----#
tree1 = ttk.Treeview(window)
tree1.heading("#0",text="Food Item Name")
tree1.grid(row=4,column=0,columnspan=4,padx=(10,0),pady=10,sticky='NSEW')
tree1.bind('<ButtonRelease-1>', selectItem)

b1 = ttk.Button(window,text='Reload Data',command=reloadData)
b1.grid(row=8,column=0,columnspan=3,pady=10)

#----- Credits -----#
creditMsg = tk.Message(window, text='PEW CODES')
creditMsg.config(font=("Courier", 8))
creditMsg.place(relx=0.98,rely=0.98,anchor="se")

listOfFoodItems = loadData(fileName)
updateTreeView()
window.after_idle(initMsg, window, "Welcome to Food App!")
window.mainloop()                                                               # Main loop to wait for events

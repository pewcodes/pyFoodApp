# pyFoodAppGUI <img alt="GitHub" src="https://img.shields.io/github/license/pewcodes/pyFoodAppGUI.svg">

### Admin Application
**System for admins to insert, delete, read items through database instead of .txt file**

1. The Admin Application will run an initial check for presence of sqlite database file. If not present, it will initialize and create a table in the database with initial data read from .txt file. 
2. Upon keying data for a new item record for and clicking `Add`, data will be inserted into database table.
3. Upon keying the name for an existing item and clicking `Delete`, data will be deleted from database table.
4. A message pop up will display upon successful insertion or deletion.

![ssadmin](https://user-images.githubusercontent.com/33170550/53583167-f8c39080-3bbb-11e9-9526-3a0f5e615836.png)

### User Application
**System that displays information to users from database**

1. Loads in data from database and displays items in `treeview` and `textbox fields`. 
2. Filters price based on the name & category based on `scale` which indicates max price range.

![ssuser](https://user-images.githubusercontent.com/33170550/53584082-cfa3ff80-3bbd-11e9-8ad0-689db554ace7.png)

### Overview of Application Functions

![ssabtadmin](https://user-images.githubusercontent.com/33170550/53583164-f82afa00-3bbb-11e9-8138-7133ffdbe69c.png)
![ssabtuser](https://user-images.githubusercontent.com/33170550/53583165-f82afa00-3bbb-11e9-8786-a650b033bcb5.png)

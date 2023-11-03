
# Libraries used
from tkinter import *
from time import *
from random import *
import mysql.connector as conn

# Variables defined
l = {}
character = "  * "
character_list = ["  * ", "  ☺ ", "  ■ ", "  ▲ "]
npc_dict = {"npc1": "■", "npc2": "▲", "npc3": "☢", "npc4": "◉"}
order_list = {"maze": 21, "maze1": 10}
boundary_characters = [" ┉  ", "  ╎  ", "  =  ", "  ↲  ", "  Ⅱ  ", "  ↴  ", "  ↱  ", "  ―  ", "  ↳  ", "  l  "]
floor = boundary_characters[0]
wall = boundary_characters[1]
Goal = "  X  "
movable_space = "       "
game_win = "not defined yet"
end_time = 0
start_time = 0
Leaderboard = {}
create_map_start = 0
leaderboard_type = "not set yet"
Pacman_Leaderboard = {}
Maze_Leaderboard = {}
leaderboard_displayed = 1
num = """1 = One	2 = Two
3 = Three	4 = Four
5 = Five	6 = Six
7 = Seven	8 = Eight
9 = Nine	10 = Ten
11 = Eleven	12 = Twelve
13 = Thirteen	14 = Fourteen
15 = Fifteen	16 = Sixteen
17 = Seventeen	18 = Eighteen
19 = Nineteen	20 = Twenty
"""
playing = 0


# to create a dictionary with numbers as keys and it's word format as values
number_and_word = {}
s = {2: "Twenty", 3: "Thirty", 4: "Forty", 5: "Fifty", 6: "Sixty", 7: "Seventy", 8: "Eighty", 9: "Ninety"}  # primary digits
for i in range(len(num)-1):  # block to get the first 19 digits from the string "num"
    start_found = 0
    if num[i].isnumeric() and not num[i+1].isnumeric() and not num[i-1].isnumeric():  # Checking if the number given is single digit
        for j in range(i, len(num)):
            if num[j].isalpha() and start_found != 1:  # Finding the starting index of the word
                start_found = 1
                start = j
            if not num[j].isalpha() and start_found == 1:  # Finding the end index of the word
                start_found = 0
                end = j
                number_and_word[num[i]] = num[start: end]
                break
    if num[i].isnumeric() and num[i+1].isnumeric() and not num[i+2].isnumeric(): # Checking if the number is two digits
        for j in range(i, len(num)):
            if num[j].isalpha() and start_found != 1:  # Finding the starting index
                start_found = 1
                start = j
            if not num[j].isalpha() and start_found == 1:  # Finding the end index
                start_found = 0
                end = j
                number_and_word[num[i]+num[i+1]] = num[start: end]
                break
for j in range(20, 100):
    a = f"{j}"
    if int(a[1]) == 0:  # Checks whether the number being held by j is divisible by 10
        number_and_word[a] = s[int(a[0])]
    else:  # if j is not divisible by 10
        number_and_word[a] = s[int(a[0])] + "_" + number_and_word[(a[1])]
number_and_word["100"] = "One_hundred"


# connection to mysql
try:

    print("Connecting to Mysql...")
    mydb = conn.connect(host="localhost", user="root", password="")  # Enter password here
    print("Established connection!")
    cur = mydb.cursor()
    # Creating the required tables
    cur.execute("show databases;")
    print("Checking for pacamaze database...")
    if ("Pacamaze",) not in cur.fetchall():  # checks whether the database is already created or not
        print("Pacamaze not found \n Creating Pacamaze")  # creates the required tables if database not found
        cur.execute("create database pacamaze;")
        cur.execute("use Pacamaze;")
        cur.execute("create table Pacman_leaderboard(Name Varchar(6), Score varchar(15));")  # Table to store Pacman leaderboard details
        cur.execute("Create table Maze_leaderboard(Name Varchar(6), Score varchar(15));")  # Table to store Maze leaderboard details
        cur.execute("Create table Pacman_maps(One Char(5));")  # Table to store Pacman maps
        cur.execute("Create table Maze_maps(One Char(5));")  # Table to store Maze maps
        for i in number_and_word:  # loop to create a hundred columns to store each element of the display matrix
            if i != "1":
                cur.execute(f"Alter table Pacman_maps add ({number_and_word[i]} char(5));")
        for i in number_and_word:
            if i != "1":
                cur.execute(f"Alter table Maze_maps add ({number_and_word[i]} char(5));")
    else:  # acceses the database if it is found
        print("pacamaze found!")
        cur.execute("use pacamaze;")

    # Retrieving Leaderboard data
    print("Retrieving Leaderboard data from Mysql database")
    cur.execute("Select * from maze_leaderboard;")
    started = 0
    for i in cur.fetchall():
        if i[0] not in Maze_Leaderboard:  # Checking whether the name is already present in the Maze Leaderboard dictionary
            started = 0
        if started == 0:  # adds the name score pair into the leaderboard if it's not already present
            Maze_Leaderboard[i[0]] = i[1]
            started = 1
        else:  # executes when the name of the given record is already present and compares to pick higher score
            if i[1] < Maze_Leaderboard[i[0]]:
                Maze_Leaderboard[i[0]] = i[1]
    print("Maze leaderboard data received: ", Maze_Leaderboard)
    cur.execute("Select * from Pacman_leaderboard;")
    started = 0
    for i in cur.fetchall():
        if i[0] not in Pacman_Leaderboard:
            started = 0
        if started == 0:  # adds the name score pair into the leaderboard if it's not already present
            Pacman_Leaderboard[i[0]] = i[1]
            started = 1
        else:  # executes when the name of the given record is already present and compares to pick higher score
            if i[1] < Pacman_Leaderboard[i[0]]:
                Pacman_Leaderboard[i[0]] = i[1]
    print("Pacman leaderboard data received: ", Pacman_Leaderboard)

except:
    print("Connection failed!")


# declare and configure window

window = Tk()
window.configure(width=500, height=500)


# Basic Functions defined


def window_clear():  # to clear the contents in the window
    print("Window cleared")
    to_clear = window.pack_slaves()
    for i in to_clear:
        i.destroy()


def create(n, bg):  # to create a matrix of nth order and having movable spaces as "bg"
    print("Creating the matrix..")
    for i in range(1, n ** 2 + 1):  # iterates over n**2 elements since a square matrix is being created
        if n % 2 == 0:  # Checks whether the order is even
            if i == ((n ** 2) / 2) - n / 2:
                l[i] = character  # placing the character
            else:
                l[i] = bg  # assigning the movable spaces
        else:  # If order is odd
            if i == (n ** 2 + 1) / 2:
                l[i] = character  # placing the character
            else:
                l[i] = bg  # assigning the movable spaces
    # To place the boundaries around the matrix
    for i in range(1, n ** 2 + 1):
        if i in range(n ** 2 - n + 1, n ** 2):  # Bottom row
            l[i] = "  =  "
        if i in range(2, n):  # Top row
            l[i] = "  =  "
        elif (i - 1) % n == 0 and i != n ** 2 - n + 1 and i != 1:  # left column
            l[i] = "  Ⅱ  "
        elif i % n == 0 and i != n and i != n ** 2:  # right column
            l[i] = "  Ⅱ  "
        elif i == 1:  # left top corner
            l[i] = "  ↱  "
        elif i == n ** 2:  # right bottom corner
            l[i] = "  ↲  "
        elif i == n:  # right top corner
            l[i] = "  ↴  "
        elif i == n ** 2 - n + 1:  # left bottom corner
            l[i] = "  ↳  "
    print("Matrix Created")
    return l, n


lnd, order = create(10, "  _  ")  # Creating a matrix of 10th order and movable spaces as "  _  "


def display_with_index(): # to create a matrix and and to convert blankspaces into
    # ordered numbers for user-map creation interface
    print("Converting the blankspaces in the matrix into numeric digits..")
    index_value = 1
    for i in lnd:
        # to make sure loop iterates over only movable spaces and not the boundaries
        if i in range(12, 90) and i not in range(11, 99, 10) and i not in range(10, 100, 10):
            if index_value < 10:
                lnd[i] = str(f"  {index_value}   ")
            else:
                lnd[i] = str(f"  {index_value} ")
            index_value += 1
    return lnd


def display():
    print("displaying the matrix")
    if game_win != 1:  # checks if the game is still being played or not
        # this condition is to prevent any random display pop ups while the user is in the main menu
        print("Matrix displayed")
        row = ""
        for i in lnd:  # iterates over the matrix
            if i % order == 0 and i != 1:
                row += f"{lnd[i]}"
                Label(window, text=row).pack()  # packing the row as a label widget
                # after the last element in the row is added
                row = ""  # clearing the row variable and making it available for the next row
            else:
                row += f"{lnd[i]}"  # to concatenate all the elements in a row
    else:
        print("#####Can't display matrix since game isn't being played!#####")


def find_player():  # iterates over the matrix to find the location of the player
    for i in l:
        if l[i] == character:
            print("Updating player location: ",i)
            return i
    else:
        print("~   Can't find player location   ~ ")
        game_over()  # this block is executed when the player location can't be found


def time_convert(sec):  # converts time into 00:00:00 format
    global mins
    global hours
    global secs
    global score
    mins = sec // 60
    secs = sec % 60
    hours = mins // 60
    mins = mins % 60
    a = str(secs)
    if secs < 10:
        Label(window,
              text=f"Time taken: {int(hours)}:{int(mins)}:0{a[:3]}").pack()
        score = f"{int(hours)}:{int(mins)}:0{a[:3]}"
    else:
        Label(window,
            text=f"Time taken: {int(hours)}:{int(mins)}:{a[:3]}").pack()
        score = f"{int(hours)}:{int(mins)}:{a[:3]}"


def save_score(x):
    global Maze_Leaderboard
    global Pacman_Leaderboard
    global score
    if len(x) > 6:
        temp_mess = Label(window, text="Name more than 6 characters are not allowed!\n")  # restriction on name length is kept
        # so as to prevent character spacing issue in the leaderboard menu
        temp_mess.pack()
        window.update_idletasks()
        window.after(3000, temp_mess.destroy())  # to make the program wait for 3 seconds before destroying label
    else:
        if leaderboard_type == "maze":
            if x in Maze_Leaderboard: # checks if the name is already present in the leaderboard
                print("Checking if the score achieved is high score or not")
                if score > Maze_Leaderboard[x]:  # checks if the score is higher than previous high score
                    print("High score not achieved ! deploying temp warning message :)")
                    temp_mess = Label(window, text="You haven't hit your high score yet!")
                    temp_mess.pack()
                    window.update_idletasks()
                    window.after(3000, temp_mess.destroy())
                else:
                    Maze_Leaderboard[x] = score  # if the score achieved is the user's high score
                    print("Achieved high score!!!")
                    slaves = window.pack_slaves()
                    for i in window.pack_slaves():  # deletes the input box  and the save score label
                        a_label = str(slaves[0])[:7]
                        b_label = int(str(slaves[0])[7:])
                        if str(i) == a_label + str(b_label + 3):
                            i.destroy()
                        if str(i) == a_label + str(b_label + 2):
                            i.destroy()
                    for i in slaves:
                        if "entry" in str(i):
                            i.destroy()
                            break
                    for i in slaves:
                        if "button" in str(i):
                            i.destroy()
                            break
                    temp_mess = Label(window, text="Your score has been saved!")
                    temp_mess.pack()
                    window.update_idletasks()
                    window.after(3000, temp_mess.destroy())
                    # Inserting the scores into sql
                    cur.execute(f"Insert into maze_leaderboard values('{x}', '{Maze_Leaderboard[x]}');")
                    print("Entering score data into mysql...")
                    mydb.commit()
            else:
                print("New user detected!!")
                Maze_Leaderboard[x] = score
                slaves = window.pack_slaves()
                for i in window.pack_slaves():
                    a_label = str(slaves[0])[:7]
                    b_label = int(str(slaves[0])[7:])
                    if str(i) == a_label + str(b_label + 3):
                        i.destroy()
                    if str(i) == a_label + str(b_label + 2):
                        i.destroy()
                for i in slaves:
                    if "entry" in str(i):
                        i.destroy()
                        break
                for i in slaves:
                    if "button" in str(i):
                        i.destroy()
                        break
                temp_mess = Label(window, text="Your score has been saved!")
                temp_mess.pack()
                window.update_idletasks()
                window.after(3000, temp_mess.destroy())
                # Inserting the scores into sql
                cur.execute(f"Insert into maze_leaderboard values('{x}', '{Maze_Leaderboard[x]}');")
                print("Entering score data into mysql...")
                mydb.commit()
        else:
            if x in Pacman_Leaderboard:
                if score > Pacman_Leaderboard[x]:
                    temp_mess = Label(window, text="You haven't hit your high score yet!")
                    temp_mess.pack()
                    window.update_idletasks()
                    window.after(3000, temp_mess.destroy())
                else:
                    Pacman_Leaderboard[x] = score
                    slaves = window.pack_slaves()
                    for i in window.pack_slaves():
                        a_label = str(slaves[0])[:7]
                        b_label = int(str(slaves[0])[7:])
                        if str(i) == a_label + str(b_label + 3):
                            i.destroy()
                        if str(i) == a_label + str(b_label + 2):
                            i.destroy()
                    for i in slaves:
                        if "entry" in str(i):
                            i.destroy()
                            break
                    for i in slaves:
                        if "button" in str(i):
                            i.destroy()
                            break
                    save_message = Label(window, text="Your score has been saved!")
                    save_message.pack()
                    # Inserting the scores into sql
                    cur.execute(f"Insert into Pacman_leaderboard values('{x}', '{score}');")
                    mydb.commit()
            else:
                Pacman_Leaderboard[x] = score
                slaves = window.pack_slaves()
                for i in window.pack_slaves():
                    a_label = str(slaves[0])[:7]
                    b_label = int(str(slaves[0])[7:])
                    if str(i) == a_label + str(b_label + 3):
                        i.destroy()
                    if str(i) == a_label + str(b_label + 2):
                        i.destroy()
                for i in slaves:
                    if "entry" in str(i):
                        i.destroy()
                        break
                for i in slaves:
                    if "button" in str(i):
                        i.destroy()
                        break
                save_message = Label(window, text="Your score has been saved!")
                save_message.pack()
                # Inserting the scores into sql
                cur.execute(f"Insert into pacman_leaderboard values('{x}', '{score}');")
                mydb.commit()


def show_leaderboard():
    global leaderboard_displayed
    # Sort maze leaderboard according to scores
    if leaderboard_displayed != 1:
        # Retrieving Leaderboard data
        cur.execute("Select * from maze_leaderboard;")
        started = 0
        for i in cur.fetchall():
            if i[0] not in Maze_Leaderboard:
                started = 0
            if started == 0:
                Maze_Leaderboard[i[0]] = i[1]
                started = 1
            else:
                if i[1] < Maze_Leaderboard[i[0]]:
                    Maze_Leaderboard[i[0]] = i[1]
        cur.execute("Select * from Pacman_leaderboard;")
        started = 0
        for i in cur.fetchall():
            if i[0] not in Pacman_Leaderboard:
                started = 0
            if started == 0:  # adds the name score pair into the leaderboard if it's not already present
                Pacman_Leaderboard[i[0]] = i[1]
                started = 1
            else:
                if i[1] < Pacman_Leaderboard[i[0]]:
                    Pacman_Leaderboard[i[0]] = i[1]
    print("-->The Pacman leaderboard obtained from sql is ", Pacman_Leaderboard)
    print("-->The Maze leaderboard obtained from sql is ", Maze_Leaderboard)
    maze_leaderboard_sorted = {}
    strtelement = 0
    while Maze_Leaderboard != {}:
        for i in Maze_Leaderboard:
            strtelement = Maze_Leaderboard[i]
            name = i
            break
        for j in Maze_Leaderboard:
            if Maze_Leaderboard[j] < strtelement:
                strtelement = Maze_Leaderboard[j]
                name = j
        del Maze_Leaderboard[name]
        maze_leaderboard_sorted[name] = strtelement
    # Sort pacman leaderboard according to scores
    pacman_leaderboard_sorted = {}
    strtelement = 0
    while Pacman_Leaderboard != {}:
        for i in Pacman_Leaderboard:
            strtelement = Pacman_Leaderboard[i]
            name = i
            break
        for j in Pacman_Leaderboard:
            if Pacman_Leaderboard[j] < strtelement:
                strtelement = Pacman_Leaderboard[j]
                name = j
        del Pacman_Leaderboard[name]
        pacman_leaderboard_sorted[name] = strtelement
    window_clear()
    Label(window, text="LEADERBOARD").pack()
    Label(window, text="\t\t\tMaze Leaderboard\t\t\t").pack()
    Label(window, text="\t\tName\t\tTime Taken\t\t").pack()
    for i in maze_leaderboard_sorted:
        Label(window, text=f"\t{i}\t\t{maze_leaderboard_sorted[i]}\t\t").pack()
    Label(window, text="\n").pack()
    Label(window, text="\t\t\tPacman Leaderboard\t\t\t").pack()
    Label(window, text="\t\tName\t\tTime Taken\t\t").pack()
    for i in pacman_leaderboard_sorted:
        Label(window, text=f"\t{i}\t\t{pacman_leaderboard_sorted[i]}\t\t").pack()
    Button(window, text="Main menu", command=lambda: main_menu()).pack()
    leaderboard_displayed = 0


def save_map_sql():
    # to check if the character was placed or not
    global character
    savable = 0
    for i in lnd:
        if "*" in lnd[i]:
            savable = 1
            break
    else:
        temp_mess = Label(window, text="Please place the character(*) before saving!\n")
        temp_mess.pack()
        window.update_idletasks()
        window.after(2000, temp_mess.destroy())
    if savable == 1:
        # to convert the numbered matrix back to blank
        movable_space = "       "
        for i in lnd:
            for j in lnd[i]:
                if j.isnumeric():
                    lnd[i] = movable_space
                    break
        # creating the insert command  to insert the map into database
        command = "insert into Maze_maps values ("
        started = 0
        for i in lnd:
            if started == 0:
                a = f"{lnd[i]}"
                b = "'"
                b += a + "'"
                command += f"{b}"
                started = 1
            else:
                a = f"{lnd[i]}"
                b = "'"
                b += a + "'"
                command += f",{b}"
        command += ");"
        # execution of command
        cur.execute(command)
        mydb.commit()
        # temporary message to denote that the map has been saved
        temp_mess = Label(window, text="Your Map has been Saved !\n")
        temp_mess.pack()
        window.update_idletasks()
        window.after(2000, temp_mess.destroy())


#                                                  Maps


def default_maze():
    window_clear()
    global game_win
    game_win = 0
    global lnd
    global order
    lnd, order = create(10, "  _  ")
    display()
    window.bind("<w>", move_up)
    window.bind("<s>", move_down)
    window.bind("<a>", move_left)
    window.bind("<d>", move_right)
    Label(window, text="\n").pack()
    Button(window, text="Main menu", command=lambda: main_menu()).pack()
    Label(window, text="\n").pack()


def maze_level_01():
    global playing
    playing = 1
    global leaderboard_type
    leaderboard_type = "maze"
    global start_time
    start_time = time()
    global game_win
    game_win = 0
    window_clear()
    movable_space = "       "
    l, n = create(10, movable_space)
    wall_locations = (68, 58, 48, 38, 28, 23, 33, 43, 46)
    floor_locations = (72, 73, 74, 75, 76, 77, 78, 27, 26, 25, 24, 54, 55, 56)
    for i in l:
        if l[i] == character:
            l[i] = movable_space
            l[82] = character
    for i in l:
        if i in wall_locations:
            l[i] = boundary_characters[1]
        if i in floor_locations:
            l[i] = boundary_characters[0]
        if i == 45:
            l[i] = Goal
        if i in (78,):
            l[i] = "  ↲  "
        if i in (28,):
            l[i] = "  ↴  "
        if i in (23,):
            l[i] = "  ↱  "
        if i in (53,):
            l[i] = "  ↳  "
        if i in (56,):
            l[i] = "  ↲  "
    display()
    window.bind("<w>", move_up)
    window.bind("<s>", move_down)
    window.bind("<a>", move_left)
    window.bind("<d>", move_right)


def user_creates_map():
    global lnd
    global order
    global create_map_start
    # Creates the blank landscape and inserts the indexes
    if create_map_start == 0:
        lnd, order = create(10, "  _  ")
        lnd = display_with_index()
    # declaring necessary variables
    global game_win
    global q
    game_win = 0
    q = 0
    # nested function that saves the character into the landscape

    def save():
        # checks whether each character is defined by the program or not
        if char.get() in "l=X*":
            # iterates through each element in the landscape
            for i in lnd:
                for m in "1234567890":
                    # checks whether the element has numeric characters (basically checks whether the element is an
                    # index or not
                    if m in lnd[i].strip():
                        # checks if the entered index is valid, checks if the current element undergoing the
                        # iteration is the same as entered index
                        if int(index.get()) in range(1, 65) and int(lnd[i].strip()) == int(index.get()):
                            lnd[i] = f"  {char.get()}  "
                            global create_map_start
                            create_map_start = 1
                            window_clear()
                            user_creates_map()
                            print("Ignore the error lol")

    window_clear()
    Label(window, text="CREATE YOUR OWN MAP").pack()
    display()
    Label(window, text="Allowed characters are :  l, =, X, *").pack()
    Label(window, text="\n").pack()
    Label(window, text="Enter index value").pack()
    index = Entry(window)
    index.pack()
    Label(window, text="\n").pack()
    Label(window, text="Enter the character").pack()
    char = Entry(window)
    char.pack()
    Label(window, text=" ").pack()
    Button(window, text="Save", command=lambda: save()).pack()
    Label(window, text=" ").pack()
    Button(window, text="Save map", command=lambda: save_map_sql()).pack()
    Label(window, text=" ").pack()
    Button(window, text="Main menu", command=lambda: main_menu()).pack()
    Label(window, text=" ").pack()


def play_maze(m_t):
    global playing
    playing = 1
    global leaderboard_type
    leaderboard_type = "maze"
    global start_time
    start_time = time()
    global game_win
    game_win = 0
    window_clear()
    global movable_space
    movable_space = "  _  "
    l, n = create(10, movable_space)
    for i in l:
        if l[i] != "":
            l[i] = m_t[i-1]
        if "*" in l[i]:
            l[i] = character
        if l[i] == "":
            l[i] = movable_space
        for j in boundary_characters:
            if j.strip() in l[i]:
                l[i] = j
        if Goal.strip() in l[i]:
            l[i] = Goal
    display()
    if playing == 1:
        window.bind("<w>", move_up)
        window.bind("<s>", move_down)
        window.bind("<a>", move_left)
        window.bind("<d>", move_right)

#                                                   PACMAN


def randomize_npc_movement():  # needs work
    global l
    for i in range(62, 13, -20):
        for j in range(i, i+8):
            if l[j] in npc_dict.values():
                a = choice("lr")
                if a == "l" and l[j-1] != Goal and l[j-1] not in boundary_characters:
                    print(l[j], "has moved from", j, "to", j-1)
                    l[j - 1] = l[j]
                    l[j] = movable_space
                if a == "r" and l[j + 1] != Goal and l[j + 1] not in boundary_characters:
                    print(l[j], "has moved from", j, "to", j + 1)
                    l[j + 1] = l[j]
                    l[j] = movable_space
                break
    global lnd
    lnd = l


def pacman_level_01():
    global playing
    playing = 1
    global leaderboard_type
    leaderboard_type = "pacman"
    global start_time
    start_time = time()
    global game_win
    game_win = 0
    # Block to set up the map, goal location and character location
    window_clear()
    movable_space = "       "
    l, n = create(10, movable_space)
    goal_index = choice([randrange(12, 20), randrange(22, 30)])
    l[goal_index] = Goal
    a, b, c = randrange(72, 80), randrange(52, 60), randrange(32, 40)
    d, e, f = a, b, c
    while (d, e, f) == (a, b,c ):
        d, e, f = randrange(72, 80), randrange(52, 60), randrange(32, 40)
    for i in l:
        if l[i] == character:
            l[i] = movable_space
            l[82] = character
        for j in range(72, 23, -20):
            if i in range(j, j+8):
                l[i] = floor
        if i in (a, b, c, d, e, f):
            l[i] = movable_space
    # Block to set up npcs in the desired locations
    m = 1
    if m < 5:
        for e in range(62, 13, -20):
            if e != goal_index:
                avail_location = []
                for i in range(e, e+8):
                    if i != goal_index:
                        avail_location += [i,]
                a = choice(avail_location)
                print(a)
                l[a] = npc_dict["npc" + f"{m}"]
                m += 1
    # Block to sense player movement
    global lnd
    lnd = l
    display()
    Label(window, text=" ").pack()
    Button(window, text="Main menu", command=lambda: main_menu()).pack()
    Label(window, text=" ").pack()
    window.bind("<w>", move_up)
    window.bind("<s>", move_down)
    window.bind("<a>", move_left)
    window.bind("<d>", move_right)


#                                                   Victory_Page


def victory():
    global playing
    playing = 0
    global game_win
    game_win = 1
    end_time = time()
    time_elapsed = end_time - start_time
    window_clear()
    x = "\n" * 5
    y = "\t"
    time_convert(time_elapsed)
    Label(window, text=f"{y}Congrats you have won!! {y}{y}{x}").pack()
    Label(window, text="\n").pack()
    global Name_entry
    Label(window, text="Enter your name here: ").pack()
    Name_entry = Entry(window)
    Name_entry.pack()
    Label(window, text="\n").pack()
    Button(window, text="Save Score", command=lambda: save_score(Name_entry.get())).pack()
    Label(window, text="\n").pack()
    Button(window, text="Leaderboard", command=lambda: show_leaderboard()).pack()
    Label(window, text="\n").pack()
    Button(window, text="Main Menu", command=lambda: main_menu()).pack()
    Label(window, text="\n").pack()

#                                                  GAME OVER


def game_over():
    global playing
    playing = 0
    global game_win
    game_win = 1
    end_time = time()
    time_elapsed = end_time - start_time
    window_clear()
    x = "\n" * 5
    y = "\t"
    time_convert(time_elapsed)
    Label(window, text=f"{y}{y}GAME OVER!{y}{y}{x}").pack()
    Label(window, text="\n").pack()
    Button(window, text="Main Menu", command=lambda: main_menu()).pack()
    Label(window, text="\n").pack()


#                                                  Keyboard input


def move_up(event):
    global game_win
    global lnd
    global playing
    if playing == 1 and game_win != 1:
        loc = find_player()
        if lnd[loc - order] in npc_dict.values():  #finish npc movement then check?
            lnd[loc] = movable_space
            window_clear()
            display()
            window.update_idletasks()
            window.after(500, game_over())

        if lnd[loc - order] == Goal:
            lnd[loc - order] = lnd[loc]
            lnd[loc] = movable_space
            game_win = 1
            window_clear()
            display()
            victory()

        elif loc - order in lnd and lnd[loc - order] not in boundary_characters and lnd[
            loc - order] != Goal and game_win != 1:
            lnd[loc - order], lnd[loc] = lnd[loc], lnd[loc - order]
            if leaderboard_type == "pacman":
                randomize_npc_movement()
            window_clear()
            display()
            Button(window, text="Main menu", command=lambda: main_menu()).pack()
            find_player()


def move_down(event):
    global game_win
    global lnd
    global playing
    if playing == 1 and game_win != 1:
        loc = find_player()
        if lnd[loc + order] in npc_dict.values():
            lnd[loc] = movable_space
            window_clear()
            display()
            window.update_idletasks()
            window.after(500, game_over())

        if lnd[loc + order] == Goal:
            game_win = 1
            lnd[loc] = movable_space
            window_clear()
            display()
            victory()

        elif loc + order in lnd and lnd[loc + order] not in boundary_characters and lnd[
            loc + order] != Goal and game_win != 1:
            lnd[loc + order], lnd[loc] = lnd[loc], lnd[loc + order]
            if leaderboard_type == "pacman":
                randomize_npc_movement()
            window_clear()
            display()
            Button(window, text="Main menu", command=lambda: main_menu()).pack()
            find_player()


def move_left(event):
    global game_win
    global lnd
    global playing
    if playing == 1 and game_win != 1:
        loc = find_player()
        if lnd[loc - 1] in npc_dict.values():
            lnd[loc] = movable_space
            window_clear()
            display()
            window.update_idletasks()
            window.after(500, game_over())

        if lnd[loc - 1] == Goal:
            game_win = 1
            lnd[loc - 1] = lnd[loc]
            lnd[loc] = movable_space
            window_clear()
            display()
            victory()

        elif loc - 1 in lnd and lnd[loc - 1] not in boundary_characters and lnd[loc - 1] != Goal and game_win != 1:
            lnd[loc - 1], lnd[loc] = lnd[loc], lnd[loc - 1]
            if leaderboard_type == "pacman":
                randomize_npc_movement()
            window_clear()
            display()
            Button(window, text="Main menu", command=lambda: main_menu()).pack()
            find_player()


def move_right(event):
    global game_win
    global lnd
    global playingdda
    if playing == 1 and game_win != 1:
        loc = find_player()
        if lnd[loc + 1] in npc_dict.values():
            lnd[loc] = movable_space
            window_clear()
            display()
            window.update_idletasks()
            window.after(500, game_over())

        if lnd[loc + 1] == Goal:
            game_win = 1
            lnd[loc + 1] = lnd[loc]
            lnd[loc] = movable_space
            window_clear()
            display()
            victory()

        elif loc + 1 in lnd and lnd[loc + 1] not in boundary_characters and lnd[loc + 1] != Goal and game_win != 1:
            lnd[loc + 1], lnd[loc] = lnd[loc], lnd[loc + 1]
            if leaderboard_type == "pacman":
                randomize_npc_movement()
            window_clear()
            display()
            Button(window, text="Main menu", command=lambda: main_menu()).pack()
            find_player()


#                                                      Main Menu

def maze_menu():
    window_clear()
    # preset maps present in the program
    Label(window, text=" ").pack()
    Label(window, text="\t  Choose a level\t\t").pack()
    Label(window, text=" ").pack()
    Button(window, text="Blank map", command=lambda: default_maze()).pack()
    Label(window, text=" ").pack()
    Button(window, text="Map: 01", command=lambda: maze_level_01()).pack()
    Label(window, text=" ").pack()
    # to retrieve all the maps saved in the database and display before the user
    cur.execute("select * from maze_maps;")
    x = 1
    for i in cur.fetchall():
        Button(window, text=f"User created map: {x}", command=lambda: play_maze(i)).pack()
        Label(window, text=" ").pack()
        x += 1
    # to allow the user to create maps
    Button(window, text="Create your own map", command=lambda: user_creates_map()).pack()
    Label(window, text=" ").pack()
    Button(window, text="Main Menu", command=lambda: main_menu()).pack()
    Label(window, text=" ").pack()


def pacman_menu():
    window_clear()
    Label(window, text="\n  Choose a map  \n").pack()
    Button(window, text="Level 01", command=lambda: pacman_level_01()).pack()
    Label(window, text=" ").pack()
    Button(window, text="Main menu", command=lambda: main_menu()).pack()
    Label(window, text=" ").pack()


def game_selector_menu():
    window_clear()
    x = "\n" * 3
    Label(window, text=f"Choose your gamemode: {x}").pack()
    Button(window, text="Play Maze", command=lambda: maze_menu()).pack()
    Label(window, text="\n").pack()
    Button(window, text="Play Pac-Man", command=lambda: pacman_menu()).pack()
    Label(window, text="\n").pack()

def main_menu():
    global create_map_start
    create_map_start = 0
    window_clear()
    # Title Text
    x = "\n" * 10
    y = "\t" * 5
    window_main_screen_title = Label(window, text=f"{x}{y}PAC AMAZE{y}{x}")
    window_main_screen_title.pack()
    # Buttons
    Button(window, text="Play Now!", command=lambda: game_selector_menu()).pack(pady=20)
    Label(window, text="\n").pack()
    Button(window, text="Leaderboard", command=lambda: show_leaderboard()).pack()
    Label(window, text="\n").pack()
    Button(window, text="Quit", command=lambda: quit()).pack(pady=20)


# start
main_menu()
# move window center
posRight = int(window.winfo_screenwidth() / 2 - window.winfo_reqwidth() / 2)
posDown = int(window.winfo_screenheight() / 2 - window.winfo_reqheight() / 2)
window.geometry("+{}+{}".format(posRight, posDown))
window.mainloop()

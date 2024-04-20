from selenium import webdriver
from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from threading import Thread
from selenium.common.exceptions import TimeoutException
import pandas as pd
import os
import openpyxl
import fsspec

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


accs = dict()
with open("accs.txt", "r") as f:
    content = f.readlines()
    content = [line.rstrip('\n') for line in content]
    for line in content:
        user,password = line.split()
        accs[user] = password


def add_acc2():
    add_acc(user_var.get(), pass_var.get())
#print(accs)
def add_acc(usr,pw):
    with open("accs.txt", "a") as f:
        f.write(usr + ' ' + pw)
        f.write("\n")

#################
##MAIN FUNCTION##
#################

def main(user,password):
    #######################
    ##GETTING THE BROWSER##
    #######################
    browser = webdriver.Chrome()
    browser.get('https://www.instagram.com')

    #######################################
    ##ELEMENTS FOR UPDATING IN THE FUTURE##
    #######################################
    accept_1 = '//*[text()="Decline optional cookies"]' #third possibility for cookies
    username_box1 = '//*[@id="loginForm"]/div/div[1]/div/label' #username entry box
    sleep(1)
    
    ##############
    ##LOGGING IN##
    ##############
    WebDriverWait(browser, 5).until(EC.element_to_be_clickable((By.XPATH, accept_1))).click()
    username_box = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, username_box1)))
    while True:
        try:
            username_box.click()
            break
        except:
            pass

                #1.) slimpsonbart@gmail.com             2.) rankvisionagency
                #1.) bartolomejjedekrastavce            2.) blonked123
    username_box.send_keys(user)

    actions = ActionChains(browser)
    actions = actions.send_keys(Keys.TAB)
    actions.perform()
    actions = actions.send_keys(password)
    actions.perform()
    actions = actions.send_keys(Keys.ENTER)
    actions.perform()
    

    #################
    ##OPENING INBOX##
    #################
    while True:
        sleep(1)
        if browser.current_url == r'https://www.instagram.com/accounts/onetap/?next=%2F':
            browser.get('https://www.instagram.com/direct/inbox/')
            break
        else:
            pass

    #READING EXCEL
    col = column_option.get()
    df = pd.read_excel("spreadsheets//"+recipients.get(), usecols=col)
    links = set()
    for i in df.values:
        links.add(i[0])



    #FETCHING DATA (DM-ed)

    with open("dms.txt", "r") as f:
        lines = f.readlines()
        dms = [line.rstrip('\n') for line in lines]

    with open("eliminate.txt", "r") as f:
        lines = f.readlines()
        elms = [line.rstrip('\n') for line in lines]

    ##################
    #SENDING MESSAGES#
    ##################
    dm_counter = 0
    for i in links:

        if dm_counter >= 50:
            for user in accs:
                password = accs.pop(user)
                browser.close()
                return(main(user,password))
            return(browser.close())

        try:
            if i in dms or i in elms:
                continue
        except TypeError:
            continue
        dm = False

        sleep(1)
        try:
            browser.get(i)
        except:
            continue
        try:
            WebDriverWait(browser, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[text()="Message"]'))).click()
        except TimeoutException:
            with open("eliminate.txt", "a") as f:
                f.write(i)
                f.write("\n")
            continue
            
        while True:
            if "direct" in browser.current_url:
                WebDriverWait(browser, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[text()="Message..."]')))
                msg = message.get('1.0', ctk.END)
                actions.send_keys(msg)
                actions.perform()
                dm = True
                dm_counter += 1
                #print(f"dm_counter went up by 1: {dm_counter}, messaged person: {i}")
                sleep(1)
                break
        
        if dm:
            with open("dms.txt", "a") as f:
                f.write(i)
                f.write("\n")
        
            

    #wait before closing
    sleep(10)


##################
#WRAPPER FUNCTION#
##################
t = None
def wrapper():
    global t
    user = list(accs.items())[0][0]
    password = accs.pop(user)
    t = Thread(target=main,args=(user,password))
    t.start()




#######
##GUI##
#######
window = ctk.CTk()
window.geometry("525x500")

ctk.CTkLabel(window, text="IG OUTREACH TOOL", font=("helvetica",20,"bold"), text_color="#FFCC70").grid(row=0,column=2,pady=10)

####COLUMN = 0##################################################
ctk.CTkLabel(window, text="Enter Username:").grid(row=0,column=0,padx=50)
user_var = ctk.StringVar()
#user_var.set("slimpsonbart@gmail.com")
user_entry = ctk.CTkEntry(window, textvariable=user_var)
user_entry.grid(row=1,column=0)

pass_var = ctk.StringVar()
#pass_var.set("bartolomejjedekrastavce")
ctk.CTkLabel(window, text="Enter Password:").grid(row=2,column=0)
pass_entry = ctk.CTkEntry(window, textvariable=pass_var)
pass_entry.grid(row=3,column=0)
#####################################################################


#dropdown
ctk.CTkLabel(window, text="Recipients:").grid(row=1,column=2)
options = os.listdir("spreadsheets")

selected_option = ctk.StringVar()
selected_option.set(options[0])
recipients = ctk.CTkOptionMenu(window, 
                                variable=selected_option, 
                                values= options,
                                text_color="black",
                                bg_color="transparent",
                                fg_color="#b8a85e",
                                button_color="#b39f49",
                                dropdown_fg_color="#8f803f",
                                button_hover_color="#8f803f",
                                dropdown_hover_color="#8f803f",)
recipients.grid(row=2,column=2)

ctk.CTkLabel(window,text="Column:").place(x=435,y=49)
column_option = ctk.StringVar()
column_option.set("D")
column_entry = ctk.CTkEntry(window, textvariable=column_option,width=38)
column_entry.place(x=440,y=76.5)

ctk.CTkLabel(window, text="Message:").grid(row=4,column=2)
message = ctk.CTkTextbox(window, width=300,height=250)
message.grid(row=6,column=2)




button = ctk.CTkButton(window, text="SEND",
                   command=wrapper,
                   border_width=2,
                   border_color="#FFCC70",
                   bg_color="transparent",
                   fg_color="transparent",
                   hover_color="#8f803f")
button.grid(row=7,column=2,pady=10)

button2 = ctk.CTkButton(window, text="ADD",
                   command=add_acc2,
                   border_width=2,
                   border_color="#FFCC70",
                   bg_color="transparent",
                   fg_color="transparent",
                   hover_color="#8f803f")
button2.grid(row=4,column=0,pady=16)

canvas = ctk.CTkCanvas(window, 
                       width=3, 
                       height=665, 
                       bg="#FFCC70", 
                       highlightthickness=1, 
                       highlightbackground="#212121")
canvas.place(x = 176.5,y=-3)
line = canvas.create_rectangle(-1,-1,1000,1000,fill = "#212121",width=5)
canvas.update()


window.mainloop()

#!/usr/bin/env python3

from tkinter import *


class LabelledEntry:
    """ defines a class included both a label and an entry """
    def __init__(self, owner, text=""):
        self.frame = Frame(owner)
        self.entry = Entry(self.frame)
        self.label = Label(self.frame, text=text)

    def pack(self):
        self.frame.pack(side=TOP, anchor="e")
        self.entry.pack(side=RIGHT)
        self.label.pack(side=RIGHT)

    def get(self):
        return self.entry.get()


def parallelize(dictionary):
    column_list = ""
    value_list = ""

    for k in dictionary.keys():
        column_list = "{}, {}".format(column_list, k)
        value_list = "{}, '{}'".format(value_list, dictionary[k])

    return column_list[2:], value_list[2:]


def trade_action():
    markets = [
        # Market name, DB Table
        ("Finance", "bond"),
        ("Real Estate", "land"),
        ("Labor", "work"),
        ("Commodity", "food"),
        ("Debt", "note")
        ]

    sides = [
        ("Buy", "bid"),
        ("Sell", "ask")
        ]

    def buildsqlinsert():
        """ constructs a sql insert statement """
        if not selected_market.get():
            print("ERROR: Market not selected")
            return
        if not selected_side.get():
            print("ERROR: Trade side not selected")
            return

        column_values = {}

        if price_entry.get():
            column_values["price"] = price_entry.get()
        if expiration_entry.get():
            column_values["expiration"] = expiration_entry.get()

        column_list, value_list = parallelize(column_values)

        print("insert into {}_{} ({}) values ({});".format(
                        markets[selected_market.get()-1][1],
                        sides[selected_side.get()-1][1],
                        column_list,
                        value_list
                        ))
        trade_frame.destroy()

    trade_frame = Frame(root)
    trade_frame.pack()
    market_frame = LabelFrame(
                trade_frame, text="Market", relief="raised", borderwidth=3)
    market_frame.pack()

    for k, market in enumerate(markets):
        Radiobutton(
                market_frame, text=market[0],
                variable=selected_market, value=k+1).pack(anchor=W)

    side_frame = LabelFrame(
                trade_frame, text="Trade Side", relief="raised", borderwidth=3)
    side_frame.pack()

    for k, side in enumerate(sides):
        Radiobutton(
                side_frame, text=side[0],
                variable=selected_side, value=k+1).pack(anchor=W)

    parameters_frame = LabelFrame(
                trade_frame, text="Basic Parameters",
                relief="raised", borderwidth=3)
    parameters_frame.pack()

    price_entry = LabelledEntry(parameters_frame, text="Price")
    price_entry.pack()

    expiration_entry = LabelledEntry(parameters_frame, text="Expiration")
    expiration_entry.pack()

    next_button = Button(trade_frame, text="Next", command=buildsqlinsert)
    next_button.pack()


root = Tk()
root.title("Fairwinds Game")

selected_market = IntVar()
selected_side = IntVar()

main_menu = Menu(root)
root.config(menu=main_menu)

action_menu = Menu(main_menu)
action_menu.add_command(label="Create Fairian")
action_menu.add_command(label="Data Base Login Credentials")
action_menu.add_command(label="Trade", command=trade_action)
action_menu.add_command(label="Manage Labor Contracts")
action_menu.add_command(label="Demand Note Payment")
action_menu.add_command(label="Set Property Tax")

main_menu.add_cascade(label="Actions", menu=action_menu)
root.mainloop()

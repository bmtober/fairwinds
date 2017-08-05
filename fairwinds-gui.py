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


class CreateFairian(Toplevel):
    def __init__(self):
        Toplevel.__init__(self, root)
        self.transient(root)
        self.title("Create Fairian")


class LoginCredentials(Toplevel):
    def __init__(self):
        Toplevel.__init__(self, root)
        self.transient(root)
        self.title("Set Login Credentials")


class LaborContracts(Toplevel):
    def __init__(self):
        Toplevel.__init__(self, root)
        self.transient(root)
        self.title("Manage Labor Contracts")


class NotePayment(Toplevel):
    def __init__(self):
        Toplevel.__init__(self, root)
        self.transient(root)
        self.title("Demand Note Payment")


class PropertyTax(Toplevel):
    def __init__(self):
        Toplevel.__init__(self, root)
        self.transient(root)
        self.title("Set Property Tax Rate")


class TradeAction(Toplevel):
    def __init__(self):
        Toplevel.__init__(self, root)
        self.transient(root)
        self.title("Trading")

        selected_market = IntVar()
        selected_side = IntVar()

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

        market_frame = LabelFrame(
                    self, text="Market", relief="raised", borderwidth=2)
        market_frame.pack(side=TOP)

        for k, market in enumerate(markets):
            Radiobutton(
                    market_frame, text=market[0],
                    variable=selected_market, value=k+1).pack(anchor="w")

        side_frame = LabelFrame(
                    self, text="Trade Side", relief="raised", borderwidth=2)
        side_frame.pack()

        for k, side in enumerate(sides):
            Radiobutton(
                    side_frame, text=side[0],
                    variable=selected_side, value=k+1).pack(anchor=W)

        parameters_frame = LabelFrame(
                    self, text="Basic Parameters",
                    relief="raised", borderwidth=2)
        parameters_frame.pack()

        price_entry = LabelledEntry(parameters_frame, text="Price")
        price_entry.pack()

        expiration_entry = LabelledEntry(parameters_frame, text="Expiration")
        expiration_entry.pack()

        button_frame = Frame(self, borderwidth=3)
        button_frame.pack(anchor="s", side=BOTTOM)

        Button(button_frame, text="Exit", command=self.destroy).pack(side=LEFT, anchor="center")
        Button(button_frame, text="Next", command=buildsqlinsert).pack(side=LEFT, anchor="center")


class Application(Tk):

    def __init__(self):
        Tk.__init__(self)
        self.geometry("600x400")
        self.title("Fairwinds Game")

        main_menu = Menu(self)
        self.config(menu=main_menu)

        action_menu = Menu(main_menu)

        main_menu.add_cascade(label="Actions", menu=action_menu)

        action_menu.add_command(label="Create Fairian", command=CreateFairian)
        action_menu.add_command(label="Data Base Login Credentials", command=LoginCredentials)
        action_menu.add_command(label="Trade", command=TradeAction)
        action_menu.add_command(label="Manage Labor Contracts", command=LaborContracts)
        action_menu.add_command(label="Demand Note Payment", command=NotePayment)
        action_menu.add_command(label="Set Property Tax", command=PropertyTax)


root = Application()
root.mainloop()

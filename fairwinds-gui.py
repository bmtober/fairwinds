#!/usr/bin/env python3

import os
from tkinter import *


def executesql(sql):
    cmd = ('psql -q <<< "\\set VERBOSITY terse\n\\set QUIET on\n{}"'.format(sql))
    os.system(cmd)


def center_window(window, width=300, height=200):
    """ sizes and centers a window """
    # get screen width and height
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # calculate position x and y coordinates
    x = (screen_width/2) - (width/2)
    y = (screen_height/2) - (height/2)
    window.geometry('%dx%d+%d+%d' % (width, height, x, y))


class LabelledEntry:
    """ defines a class included both a label and an entry """
    def __init__(self, owner, text="", value="", show=""):
        self.frame = Frame(owner)
        self.entry = Entry(self.frame, show=show)
        self.entry.delete(0, END)
        self.entry.insert(0, value)
        self.label = Label(self.frame, text=text)

    def pack(self):
        self.frame.pack(side=TOP, anchor="e")
        self.entry.pack(side=RIGHT)
        self.label.pack(side=RIGHT)

    def get(self):
        return self.entry.get()

    def focus_set(self):
        self.entry.focus_set()


def parallelize(dictionary):
    column_list = ""
    value_list = ""

    for k in dictionary.keys():
        column_list = "{}, {}".format(column_list, k)
        value_list = "{}, '{}'".format(value_list, dictionary[k])

    return column_list[2:], value_list[2:]


class Configure(Toplevel):

    def __init__(self):
        def buildsql():
            """ constructs a sql insert statement """

            if host_name_entry.get():
                os.environ["PGHOST"] = host_name_entry.get()
            if dbname_name_entry.get():
                os.environ["PGDATABASE"] = dbname_name_entry.get()
            if fairian_entry.get():
                os.environ["PGUSER"] = fairian_entry.get()
            if password_entry.get():
                os.environ["PGPASSWORD"] = password_entry.get()

        Toplevel.__init__(self, root)
        self.transient(root)
        self.title("Configuration")
        self.geometry("250x150")

        host_name_entry = LabelledEntry(self, text="Host", value=os.environ.get("PGHOST", ""))
        host_name_entry.pack()

        dbname_name_entry = LabelledEntry(self, text="Data Base", value=os.environ.get("PGDATABASE", ""))
        dbname_name_entry.pack()

        fairian_entry = LabelledEntry(self, text="Fairian Name", value=os.environ.get("PGUSER", ""))
        fairian_entry.pack()
        fairian_entry.focus_set()

        password_entry = LabelledEntry(self, text="Password", value=os.environ.get("PGPASSWORD", ""), show="*")
        password_entry.pack()

        button_frame = Frame(self, borderwidth=3)
        button_frame.pack(anchor="s", side=BOTTOM)

        Button(button_frame, text="Exit", command=self.destroy).pack(side=LEFT, anchor="center")
        Button(button_frame, text="Ok", command=buildsql).pack(side=LEFT, anchor="center")


class CreateFairian(Toplevel):
    def __init__(self):
        def buildsql():
            """ constructs a sql insert statement """

            column_values = {}

            if fairian_entry.get():
                column_values["fairian_name"] = fairian_entry.get()
            if password_entry.get():
                column_values["passwd"] = password_entry.get()
            if email_address_entry.get():
                column_values["email_address"] = email_address_entry.get()

            column_list, value_list = parallelize(column_values)

            fairian_name = os.environ.get("PGUSER", "")
            os.environ["PGUSER"] = "anonymous"
            executesql("insert into fairian ({}) values ({});".format(
                            column_list,
                            value_list
                            ))
            os.environ["PGUSER"] = fairian_name

        Toplevel.__init__(self, root)
        self.transient(root)
        self.title("Create Fairian")
        self.geometry("250x100")

        fairian_entry = LabelledEntry(self, text="Fairian Name", value=os.environ.get("PGUSER", ""))
        fairian_entry.pack()
        fairian_entry.focus_set()

        password_entry = LabelledEntry(self, text="Password", value=os.environ.get("PGPASSWORD", ""), show="*")
        password_entry.pack()

        email_address_entry = LabelledEntry(self, text="Email Address")
        email_address_entry.pack()

        button_frame = Frame(self, borderwidth=3)
        button_frame.pack(anchor="s", side=BOTTOM)

        Button(button_frame, text="Exit", command=self.destroy).pack(side=LEFT, anchor="center")
        Button(button_frame, text="Next", command=buildsql).pack(side=LEFT, anchor="center")


class LaborContracts(Toplevel):
    def __init__(self):
        def buildsql():
            """ constructs a sql insert statement """

            if work_place_entry.get():
                work_place = "work_place = '{}'".format(work_place_entry.get())
            else:
                work_place = "active = false"


            if contract_number_entry.get():
                contract_number = contract_number_entry.get()

            executesql("update work set {} where contract_number = '{}'".format(
                        work_place, contract_number))

        Toplevel.__init__(self, root)
        self.transient(root)
        self.title("Manage Labor Contracts")
        self.geometry("350x100")

        work_place_entry = LabelledEntry(self, "Work Place")
        work_place_entry.focus_set()
        work_place_entry.pack()

        contract_number_entry = LabelledEntry(self, "Contract Serial number")
        contract_number_entry.pack()

        button_frame = Frame(self, borderwidth=3)
        button_frame.pack(anchor="s", side=BOTTOM)

        Button(button_frame, text="Exit", command=self.destroy).pack(side=LEFT, anchor="center")
        Button(button_frame, text="Next", command=buildsql).pack(side=LEFT, anchor="center")


class NotePayment(Toplevel):
    def __init__(self):
        def buildsql():
            """ constructs a sql insert statement """

            if serial_number_entry.get():
                column_values = serial_number_entry.get()

            executesql("update note set called = true where serial_number = '{}".format(
                            column_values))

        Toplevel.__init__(self, root)
        self.transient(root)
        self.title("Demand Note Payment")
        self.geometry("250x100")

        serial_number_entry = LabelledEntry(self, "Serial number")
        serial_number_entry.focus_set()
        serial_number_entry.pack()

        button_frame = Frame(self, borderwidth=3)
        button_frame.pack(anchor="s", side=BOTTOM)

        Button(button_frame, text="Exit", command=self.destroy).pack(side=LEFT, anchor="center")
        Button(button_frame, text="Ok", command=buildsql).pack(side=LEFT, anchor="center")


class TaxRate(Toplevel):
    def __init__(self):
        def buildsql():
            """ constructs a sql insert statement """

            if property_tax_entry.get():
                column_values = property_tax_entry.get()

            executesql("update fairian set mill_rate = '{}' where fairian_name = current_user;".format(
                            column_values))

        Toplevel.__init__(self, root)
        self.transient(root)
        self.title("Set Property Tax Rate")
        self.geometry("300x100")

        property_tax_entry = LabelledEntry(self, "Property tax mill rate")
        property_tax_entry.focus_set()
        property_tax_entry.pack()

        button_frame = Frame(self, borderwidth=3)
        button_frame.pack(anchor="s", side=BOTTOM)

        Button(button_frame, text="Exit", command=self.destroy).pack(side=LEFT, anchor="center")
        Button(button_frame, text="Ok", command=buildsql).pack(side=LEFT, anchor="center")


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

            executesql("insert into {}_{} ({}) values ({});".format(
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
        self.title("Fairwinds Game Query Builder")
        center_window(self, 600, 400)

        main_menu = Menu(self)
        self.config(menu=main_menu)

        action_menu = Menu(main_menu)

        main_menu.add_cascade(label="Actions", menu=action_menu)

        action_menu.add_command(label="Configuration", command=Configure)
        action_menu.add_command(label="Create Fairian", command=CreateFairian)
        action_menu.add_command(label="Trade", command=TradeAction)
        action_menu.add_command(label="Manage Labor Contracts", command=LaborContracts)
        action_menu.add_command(label="Demand Note Payment", command=NotePayment)
        action_menu.add_command(label="Set Property Tax", command=TaxRate)


root = Application()
root.mainloop()

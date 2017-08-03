#!/usr/bin/env python3

from tkinter import *

class LabelledEntry:
    def __init__(self, owner, text=""):
        self.frame = Frame(owner)
        self.entry = Entry(owner)
        self.label = Label(owner, text=text)
    def pack(self):
        self.frame.pack()
        self.entry.pack(side=RIGHT)
        self.label.pack(side=RIGHT)
    def get(self):
        return self.entry.get()


def buildsql():
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

    column_list = ""
    for c in column_values.keys():
        column_list = column_list + ", " + c
    column_list = column_list[2:]

    value_list = ""
    for c in column_values.keys():
        value_list = value_list + ", " + column_values[c]
    value_list = value_list[2:]

    print("insert into {}_{} ({}) values ({});".format(
                    markets[selected_market.get()-1][1], 
                    sides[selected_side.get()-1][1],
                    column_list,
                    value_list
                    ))
    root.destroy()

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


root = Tk()
root.title("Fairwinds Query Builder")

market_frame = LabelFrame(root, text="Market")
market_frame['relief'] = "raised"
market_frame['borderwidth'] = 2
market_frame.pack()
    
selected_market = IntVar()
    
for k, market in enumerate(markets):
    Radiobutton(market_frame, text = market[0], variable=selected_market, value=k+1).pack(anchor=W)
    
side_frame = LabelFrame(root, text="Trade Side")
side_frame['relief'] = "raised"
side_frame['borderwidth'] = 2
side_frame.pack()

selected_side = IntVar()
    
for k, side in enumerate(sides):
    Radiobutton(side_frame, text = side[0], variable=selected_side, value=k+1).pack(anchor=W)

parameters_frame = LabelFrame(root, text="Parameters", relief="raised", borderwidth=2).pack()

price_entry = LabelledEntry(parameters_frame, text="Price")
price_entry.pack()

expiration_entry = LabelledEntry(parameters_frame, text="Expiration")
expiration_entry.pack()

quantity_entry = LabelledEntry(parameters_frame, text="Quantity")
quantity_entry.pack()

ok_button = Button(root, text="OK", command=buildsql)
ok_button.pack()

root
root.mainloop()


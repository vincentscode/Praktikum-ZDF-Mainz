from tkinter import *
from _thread import start_new_thread
import sched
import time
import serial
import serial.tools.list_ports
import sys
from datetime import datetime
import math
import os
import json

window = Tk()
window.title("Tester")

command_options = ["HH:mmDD.MM", "SC:SCSC.SC", "UC:UCUC.UC", "LC:LCLC.LC"]
running = False
debug = False

if os.path.exists("config.json"):
    cfg_f = open("config.json")
    cfg = json.loads(cfg_f.read())
    cfg_f.close()
else:
    cfg = {
        'before': '',
        'after': '\r'
    }

# create elements
ent_time_lbl = Label(window, text="Interval (s):")
ent_time_var = StringVar(window)
ent_time = Entry(window, textvariable=ent_time_var)
lbx_commands_lbl = Label(window, text="Befehl:")
lbx_commands_var = StringVar(window)
lbx_commands = OptionMenu(window, lbx_commands_var, *command_options)
ent_command_time_var = StringVar(window)
ent_command_time = Entry(window, textvariable=ent_command_time_var)
ent_command_use_time_var = IntVar(window)
ent_command_use_time = Checkbutton(window, text="Systemzeit verwenden", variable=ent_command_use_time_var)
prev_label_var = StringVar(window)
prev_label = Label(window, textvariable=prev_label_var)
btn = Button(window, text="Start")

# serial connection & dummy serial (-d)
if "-d" in sys.argv:
    debug = True

if debug:
    class SerialDummy():
        def write(*_):
            pass
    print("Using dummy")
    ser = SerialDummy()
else:
    ports = list(serial.tools.list_ports.comports())
    print("Using:", ports[0].device)
    seri = serial.Serial(ports[0].device)
    class SerialWrapper():
        def __init__(self, serial_port):
            self.serial_port = serial_port
        def write(self, msg):
            before = cfg["before"]
            after = cfg["after"]
            msg = bytes(before + msg + after, "ascii")
            
            print("Sending:", msg)
            print("->", self.serial_port.write(msg))

    ser = SerialWrapper(seri)

# set default values
ent_time_var.set(str(1))
lbx_commands_var.set(command_options[0])
prev_label_var.set("Preview: -")

def roundup(x):
    return int(math.ceil(x / 5.0)) * 5

def get_time_string():
    "HH:mmDD.MM"
    d = datetime.now()
    time_string = f"{d.hour:02}:{roundup(d.minute):02}{d.day:02}.{d.month:02}"
    return time_string


# event handlers
def update_preview(*_):
    if lbx_commands_var.get() != "HH:mmDD.MM":
        prev_label_var.set("Preview: " + lbx_commands_var.get())
        ent_command_time.configure(state="disabled")
        ent_command_use_time.configure(state="disabled")
    else:
        if not ent_command_use_time_var.get() == 1:
            prev_label_var.set("Preview: " + ent_command_time_var.get())
            ent_command_time.configure(state="normal")
            ent_command_use_time.configure(state="normal")
        else:
            # get sys time
            prev_label_var.set("Preview: " + get_time_string())
            ent_command_time.configure(state="disabled")
            ent_command_use_time.configure(state="normal")
        
def update_time_preview(*_):
    if lbx_commands_var.get() == "HH:mmDD.MM":
        if not ent_command_use_time_var.get() == 1:
            prev_label_var.set("Preview: " + ent_command_time_var.get())
            ent_command_time.configure(state="normal")
        else:
            # get sys time
            prev_label_var.set("Preview: " + get_time_string())
            ent_command_time.configure(state="disabled")


def btn_command(*_):
    global running
    if running:
        running = False
        btn.configure(text="Start")
    else:
        running = True
        btn.configure(text="Stop")

# configure events
btn.configure(command=btn_command)
lbx_commands.bind("<Configure>", update_preview)
ent_command_time_var.trace("w", update_time_preview)
ent_command_use_time_var.trace("w", update_time_preview)

# add elements in grid
ent_time_lbl.grid(row=0, column=0)
ent_time.grid(row=0, column=1)
lbx_commands_lbl.grid(row=1, column=0)
lbx_commands.grid(row=1, column=1)
ent_command_time.grid(row=1, column=2)
ent_command_use_time.grid(row=1, column=3)
btn.grid(row=2, column=0)
prev_label.grid(row=2, column=1)

# scheduling
s = sched.scheduler(time.time, time.sleep)
def interval_task(sc):
    global running, ser
    if running:
        if lbx_commands_var.get() == "HH:mmDD.MM":
            update_preview()
            if not ent_command_use_time_var.get() == 1:
                ser.write(ent_command_time_var.get());
            else:
                ser.write(get_time_string());
        else:
            ser.write(lbx_commands_var.get());
    s.enter(int(ent_time_var.get()), 1, interval_task, (sc,))

s.enter(int(ent_time_var.get()), 1, interval_task, (s,))


start_new_thread(s.run, ())
window.mainloop()

import flask
from flask.helpers import flash
import flask_wtf
import wtforms
import App, Client, Utility, threading
import socket, threading, time, sys, pickle, gpiozero, datetime, json, requests, pickle
from flask import Flask, session, request, redirect, url_for
from flask.templating import render_template
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField, RadioField
import Utility
from Utility import debug_print

# LEI: What's the purpose to print those?
# print(f"{App} init")
# print(f"{Client} init")
# print(f"{Utility} init")
# print(f"{threading} init")
# print(f"{socket} init")
# print(f"{flask} init")
# print(f"{flask_wtf} init")
# print(f"{wtforms} init")
# print(f"{datetime} init")
# print(f"{json} init")
# print(f"{requests} init")
# print(f"{gpiozero} init")
# print(f"{pickle} init")
# print(f"{sys} init")

client = Client.ClientSide('CLIENT')
client._set_peer('127.0.0.1', App._get_inc_port())
App._set_out_peer(client.in_port_)

"""App._run_app()

threadpool_ = list()

thread_1 = threading.Thread(target=App._run_server)
threadpool_.append(thread_1)

thread_2 = threading.Thread(target=client.start())
threadpool_.append(thread_2)"""

def app():
    print(" * *APP STARTED")
    App.app.run(host='0.0.0.0', port=8080)

def launch_threadpool():
    threadpool_ = list()

    #print(" --Thread 1 began listen incoming")
    threadpool_.append(threading.Thread(target=client._listen_incoming))
    #print(" --Thread 2 began take action")
    threadpool_.append(threading.Thread(target=client._take_action))
    #print(" --Thread 3 began run update")
    threadpool_.append(threading.Thread(target=client._run_update))
    #print(" --Thread 4 began send back")
    threadpool_.append(threading.Thread(target=client._send_back))

    #print(" --Thread 5 began listen incoming")
    threadpool_.append(threading.Thread(target=App.server._listen_incoming))
    #print(" --Thread 6 began take action")
    threadpool_.append(threading.Thread(target=App.server._take_action))
    #print(" --Thread 7 began run update")
    threadpool_.append(threading.Thread(target=App.server._run_update))
    #print(" --Thread 8 began send back")
    threadpool_.append(threading.Thread(target=App.server._send_back))

    debug_print(True, "MASTER", f"Num threads added: {len(threadpool_)}")
    for tt in threadpool_:
        tt.start()
    
# threads = list()

# threading.Thread(target=threadpool).start()
client._start()
App.server._start()
print("Thread count: " + str(threading.active_count()))

app()
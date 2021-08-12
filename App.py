from flask import Flask, session, request, redirect, url_for
from flask.templating import render_template
from flask_wtf import FlaskForm
from Forms import Button_Change_Mode, Radio_EDIT, Radio_ON, SignUp, Radio_SEC, Button_Edit, What_Edit
import Utility, threading, time

class ServerSide(Utility.Comm):
    def __init__(self, signature):
        super(ServerSide, self).__init__(signature=signature, debug=True, msg_prefix="SERVER")
        self._def_action(self.action)
    
    def action(self, data, outgoing):
        super(ServerSide, self)._take_action(self, data, outgoing)

server = ServerSide('SERVER')

app = Flask(__name__, template_folder='HTML')
app.config['SECRET_KEY'] = '12700101202117254011200'

@app.route('/')
def render_main():
    form = Button_Edit()
    return render_template('front_page.html', form=form, title="Main")

@app.route('/edit')
def edit():
    form = What_Edit()
    return render_template('edit_page.html', form=form)

@app.route('/mode')
def mode():
    form = What_Edit()
    return render_template('edit_page.html', form=form)

@app.route('/edit_man')
def edit_man():
    print("Edit man")
    server._append_out(Utility.WebInfo(2, [], [], [True, True, True, True]))
    return "Edit man"

@app.route('/edit_sch')
def edit_sch():
    print("Edit man")
    server._append_out(Utility.WebInfo(2, [], [], [False, False, False, True]))
    return "Edit sch"

@app.route('/edit_auto')
def edit_auto():
    return "Edit auto"

@app.route('/', methods=("GET", "POST"))
def main_action():
    print("home acted")
    form = Button_Edit()
    if request.method == "POST":
        if form.select.data == "edit":
            return redirect(url_for('edit'))
        if form.select.data == "mode":
            return redirect(url_for('mode'))
    return render_template('front_page.html', form=form)

@app.route('/edit', methods=("GET", "POST"))
def edit_action():
    print("edit acted")
    form = What_Edit()
    if request.method == "POST":
        print(form.select.data)
        if form.select.data == "man":
            return redirect(url_for('edit_man'))
        if form.select.data == "sch":
            return redirect(url_for('edit_sch'))
        if form.select.data == "auto":
            return redirect(url_for('edit_auto'))
    return render_template('edit_page.html', form=form)


def _get_inc_port():
    return server._get_inc_host()

def _get_out_port():
    return server._get_out_host()

def _set_out_peer(port):
    server._set_peer('127.0.0.1', port)


def _run_app():
    print(" * (SS) App run")
    app.run(port=8080, host='0.0.0.0')

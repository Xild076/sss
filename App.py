from flask import Flask, render_template, request, redirect, url_for
import Server, Utility
from Forms import *

server = Server.ServerSide()

app = Flask(__name__, template_folder='Html')
app.config['SECRET_KEY'] = '12700101202117254011200'

saved_info = Utility.WebInfo(2, [], [], [False, False, False, True])

@app.route('/')
def render_main():
    form = Button_Edit()
    return render_template('front_page.html', form=form, title="Main")

@app.route('/edit')
def edit():
    form = What_Edit()
    return render_template('edit_page.html', form=form, title="Edit")

@app.route('/mode')
def mode():
    form = What_Edit()
    return render_template('edit_page.html', form=form, title="Edit Mode")

@app.route('/edit_man')
def edit_man():
    form = What_Zone()
    return render_template('edit_man.html', form=form, title="Edit Man")

@app.route('/edit_sch')
def edit_sch():
    print("Edit man")
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

@app.route('/edit_man', methods=("GET", "POST"))
def edit_man_zone():
    print("man acted")
    form = What_Zone()
    if request.method == "POST":
        print(form.select.data)
        if saved_info.list_ons[int(form.select.data)]:
            saved_info.list_ons[int(form.select.data)] = False
        else:
            saved_info.list_ons[int(form.select.data)] = True
        server._append_out(saved_info)
    return render_template('edit_man.html', form=form, title="Edit Man")

@app.route('/edit', methods=("GET", "POST"))
def edit_action():
    print("edit acted")
    form = What_Edit()
    if request.method == "POST":
        print(form.select.data)
        if form.select.data == "man":
            saved_info.mode = 2
            return redirect(url_for('edit_man'))
        if form.select.data == "sch":
            saved_info.mode = 1
            return redirect(url_for('edit_sch'))
        if form.select.data == "auto":
            saved_info.mode = 3
            return redirect(url_for('edit_auto'))
    return render_template('edit_page.html', form=form)


def _get_inc_port():
    return server.incoming_port_

def _get_out_port():
    return server.outgoing_port_

def _set_out_peer(port):
    server._set_peer('127.0.0.1', port)


def _run_app():
    print(" * (SS) App run")
    app.run(port=8080, host='0.0.0.0')

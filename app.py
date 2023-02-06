from flask import Flask, render_template, current_app, session, redirect, url_for
import json
import os

from database.sql_provider import SQLProvider
from database.db_work import DBConnection
from database.db_work import select_dict

from auth.auth import blueprint_auth
from access import login_required
from reg.reg import blueprint_reg
from order.order import blueprint_order
from adminboard.adminboard import blueprint_adminboard

app = Flask(__name__)
app.secret_key = 'SuperKey'

app.register_blueprint(blueprint_auth, url_prefix='/auth')

app.register_blueprint(blueprint_reg, url_prefix='/reg')

app.register_blueprint(blueprint_order, url_prefix='/order')

app.register_blueprint(blueprint_adminboard, url_prefix='/adminboard')

provider = SQLProvider(os.path.join(os.path.dirname(__file__),
                                    'sql'))

app.config['db_config'] = json.load(open('configs/db_config.json'))
app.config['access_config'] = json.load(open('configs/access.json'))


@app.route('/')
@login_required
def menu_choice():
    if 'user_id' in session:
        if session.get('user_group', None):
            return redirect(url_for('blueprint_adminboard.start_admin'))  # internal_user_menu
        else:
            return render_template('external_menu.html')  # external_user_menu
    else:
        return render_template('auth.html')


@app.route('/exit')
@login_required
def exit_func():
    session.clear()
    return render_template('exit.html')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001, debug=True)

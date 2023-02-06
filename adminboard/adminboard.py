from flask import render_template, Blueprint, url_for, session, request, current_app, redirect, abort

import os
from typing import Optional, Dict
import datetime

from database.sql_provider import SQLProvider
from database.db_work import DBConnection
from database.db_work import select_dict
from database.db_work import input_dict
from cache.wrapper import fetch_from_cache
from access import login_required, group_required

blueprint_adminboard = Blueprint('blueprint_adminboard', __name__, template_folder='templates')
provider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))


@blueprint_adminboard.route('/', methods=['GET', 'POST'])
@login_required
@group_required
def start_admin():
    return render_template('admin_main.html', date=datetime.date.today())


@blueprint_adminboard.route('/newflight', methods=['GET', 'POST'])
@login_required
@group_required
def new_flight():
    if request.method == 'GET':
        return render_template('new_flight.html')
    else:
        id_fl = request.form['id_fl']
        time_out = request.form['time_out']
        time_in = request.form['time_in']
        port_out = request.form['port_out']
        port_to = request.form['port_to']
        tickets = request.form['tickets']
        price = request.form['price']
        if id_fl and time_out and time_in and port_out and port_to and tickets and price:
            _sql = provider.get('new_flight.sql', id_fl=id_fl,
                                time_out=time_out,
                                time_in=time_in,
                                port_out=port_out,
                                port_to=port_to,
                                tickets=tickets,
                                price=price)
            input_dict(current_app.config['db_config'], _sql)
            return render_template('new_flight.html', message='Рейс успешно добавлен!')
        else:
            return render_template('new_flight.html', message='Неверно заполнена форма!')


@blueprint_adminboard.route('/newlog', methods=['GET', 'POST'])
@login_required
@group_required
def new_log():
    if request.method == 'GET':
        return render_template('new_log.html')
    else:
        _all_sql = provider.get('test.sql', start_date=request.form['start_date'],
                                end_date=request.form['end_date'])
        _all = select_dict(current_app.config['db_config'], _all_sql)
        for key in range(len(_all)):
            _sql = provider.get('insert_log.sql', summa=_all[key]['SUM(tickets)'],
                                sum_price=_all[key]['SUM(sum_price)'],
                                id_fl=_all[key]['id_flight'],
                                id_finale=request.form['id_log'])
            input_dict(current_app.config['db_config'], _sql)
            print(_all[key])
        return render_template('new_log.html', message='Отчет успешно создан!')


@blueprint_adminboard.route('/logs', methods=['GET', 'POST'])
@login_required
@group_required
def logs():
    if request.method == 'GET':
        _sql = provider.get('show_logs.sql')
        show = select_dict(current_app.config['db_config'], _sql)
        session['num_logs'] = len(show)
        return render_template('logs.html', items=show, col=len(show), need=False)
    else:
        a = None
        for i in range(session['num_logs']):
            if request.form.get(f'get_value{i}'):
                a = request.form[f'need_log{i}']
                break
        _sql = provider.get('need_log.sql', need_log=a)
        out = select_dict(current_app.config['db_config'], _sql)
        return render_template('logs.html', need=out, col=len(out))

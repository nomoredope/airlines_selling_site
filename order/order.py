from flask import render_template, Blueprint, url_for, session, request, current_app, redirect

import os
from typing import Optional, Dict

from database.sql_provider import SQLProvider
from database.db_work import DBConnection
from database.db_work import select_dict
from database.db_work import input_dict
from cache.wrapper import fetch_from_cache
from access import login_required

blueprint_order = Blueprint('blueprint_order', __name__, template_folder='templates')
provider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))


@blueprint_order.route('/', methods=['GET', 'POST'])
@login_required
def start_order():
    if 'cur_search' not in session:
        all_sql = provider.get('all_flights.sql')
        session['cur_search'] = select_dict(current_app.config['db_config'], all_sql)
    if request.method == 'GET':
        basket_in = session.get('basket', {})
        return render_template('list.html', items=session['cur_search'], basket=basket_in)
    if request.method == 'POST':
        basket_in = session.get('basket', {})
        if request.form.get('clear_search'):
            all_sql = provider.get('all_flights.sql')
            session['cur_search'] = select_dict(current_app.config['db_config'], all_sql)
            return render_template('list.html', items=session['cur_search'], basket=basket_in)
        if request.form.get('search'):
            port_out = request.form.get('port_out')
            port_in = request.form.get('port_in')
            data = request.form.get('data')
            if port_out and port_in and data:
                _sql = provider.get('special_flights.sql', port_in=port_in, port_out=port_out, data=data)
            elif port_out and port_in:
                _sql = provider.get('2port.sql', port_in=port_in, port_out=port_out)
            elif data:
                _sql = provider.get('data.sql', data=data)
            else:
                all_sql = provider.get('all_flights.sql')
                session['cur_search'] = select_dict(current_app.config['db_config'], all_sql)
                return render_template('error.html')
            session['cur_search'] = select_dict(current_app.config['db_config'], _sql)
            return render_template('list.html', items=session['cur_search'], basket=basket_in)
        if request.form.get('to_basket'):
            _sql = provider.get('select_item.sql', need=request.form.get('basket_item'))
            add_to_basket(request.form.get('basket_item'), select_dict(current_app.config['db_config'], _sql)[0])
            print(session.get('basket'))
            basket_in = session.get('basket', {})
            return render_template('list.html', items=session['cur_search'], basket=basket_in)
        if request.form.get('clear'):
            clear_basket()
            return render_template('list.html', items=session['cur_search'], basket=False)
        if request.form.get('save_order'):
            save_order()
            return render_template('list.html', items=session['cur_search'], basket=False, order_complete=True)


def add_to_basket(prod_id: str, item: dict):
    curr_basket = session.get('basket', {})
    if prod_id in curr_basket:
        curr_basket[prod_id]['tickets'] += 1
    else:
        curr_basket[prod_id] = {
            'id_fl': item['id_fl'],
            'port_out': item['port_out'],
            'port_to': item['port_to'],
            'time_in': item['time_in'],
            'time_out': item['time_out'],
            'tickets': 1,
            'price': item['price']
        }
    if 'summa' not in curr_basket:
        curr_basket['summa'] = item['price']
    else:
        curr_basket['summa'] += item['price']

    session['basket'] = curr_basket
    session.permanent = True


def save_order():
    curr_basket = session.get('basket', {})
    for key in curr_basket:
        order_sql = provider.get('new_order.sql', id_user=session.get('user_id'), id_flight=curr_basket[key]['id_fl'],
                                 tickets=curr_basket[key]['tickets'], pr=curr_basket[key]['price'])
        try:
            input_dict(current_app.config['db_config'], order_sql)
        except Exception as ex:
            print(ex)
            return render_template('error.html')
    if 'basket' in session:
        session.pop('basket')


def clear_basket():
    if 'basket' in session:
        session.pop('basket')


@blueprint_order.route('/myorders', methods=['GET', 'POST'])
@login_required
def my_orders():
    _sql = provider.get('my_orders.sql', search=session['user_id'])
    src = select_dict(current_app.config['db_config'], _sql)
    return render_template('my_orders.html', orders=src, order_col=len(src))

from flask import render_template, Blueprint, url_for, session, request, current_app, abort

import os
import requests
import json
from typing import Optional, Dict

from database.sql_provider import SQLProvider
from database.db_work import DBConnection
from database.db_work import select_dict
from database.db_work import input_dict

blueprint_reg = Blueprint('blueprint_reg', __name__, template_folder='templates')
provider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))

RC_SITE_KEY = '6LcoCBokAAAAAO9yM3Xu6nPzmtsrCQreRVHDZo8d'
RC_SECRET_KEY = '6LcoCBokAAAAAJ9wUBYPmven-lDUeS6ou8GyGwPu'
RC_VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"


@blueprint_reg.route('/', methods=['GET', 'POST'])
def start_reg():
    if request.method == 'GET':
        return render_template("reg_main.html", message="", rc_key=RC_SITE_KEY)
    else:
        secret_response = request.form['g-recaptcha-response']
        verify_response = requests.post(url=f'{RC_VERIFY_URL}?secret={RC_SECRET_KEY}&response={secret_response}').json()
        if not verify_response['success']:
            abort(401)
        login = request.form.get('login')
        password = request.form.get('password')
        if login:
            if password != request.form.get('password_rep'):
                return render_template("reg_main.html", message="Неверный повтор пароля!")
            _sql = provider.get('try_reg.sql', login=login, password=password)
            try:
                input_dict(current_app.config['db_config'], _sql)
            finally:
                return render_template('reg_main.html', message='Успешная регистрация!', rc_key=RC_SITE_KEY)
        return render_template('reg_main.html', message='Повторите ввод', rc_key=RC_SITE_KEY)


def check_user():
    return

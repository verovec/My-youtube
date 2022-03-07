#!/bin/sh

flask db init
flask db migrate
flask db upgrade
flask run -p 5001 --host='0.0.0.0'

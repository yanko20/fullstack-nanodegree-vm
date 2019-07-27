from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, BikeType, BikePart, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)
engine = create_engine('sqlite:///bikeparts.db?check_same_thread=False')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.8/me"
    '''
        Due to the formatting for the result from the server token exchange we have to
        split the token first on commas and select the first index which gives us the key : value
        for the server access token then we split it on colons to pull out the actual token value
        and replace the remaining quotes with nothing so that it can be used directly in the graph
        api calls
    '''
    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = 'https://graph.facebook.com/v2.8/me?access_token=%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token

    # Get user picture
    url = 'https://graph.facebook.com/v2.8/me/picture?access_token=%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = get_user_id(login_session['email'])
    if not user_id:
        user_id = create_user(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    del login_session['facebook_id']
    del login_session['username']
    del login_session['email']
    del login_session['picture']
    del login_session['user_id']
    del login_session['provider']
    return "You have successfully been logged out."


@app.route('/')
@app.route('/catalog')
def show_bikes():
    bike_types = session.query(BikeType).all()
    bike_parts = session.query(BikePart).order_by(BikePart.id.desc()).limit(9)
    return render_template('index.html', bike_types=bike_types, bike_parts=bike_parts)


# Show a restaurant menu
@app.route('/catalog/<string:bike_type_name>/parts')
def show_bike_parts(bike_type_name):
    bike_types = session.query(BikeType).all()
    bike_type = session.query(BikeType).filter_by(name=bike_type_name).one()
    bike_parts = session.query(BikePart).filter_by(
        bike_type_id=bike_type.id).all()
    bike_part_count = len(bike_parts)
    return render_template('bike_parts.html',
                           bike_types=bike_types,
                           bike_parts=bike_parts,
                           bike_type=bike_type,
                           bike_part_count=bike_part_count)


@app.route('/catalog/<string:bike_type_name>/<string:bike_part_name>')
def show_bike_part_description(bike_type_name, bike_part_name):
    bike_type_id = session.query(BikeType).filter_by(name=bike_type_name).one().id
    bike_part = session.query(BikePart).filter_by(name=bike_part_name,
                                                  bike_type_id=bike_type_id).one()
    return render_template('bike_part_description.html',
                           bike_type_name=bike_type_name,
                           bike_part=bike_part)


@app.route('/catalog/new', methods=['GET', 'POST'])
def show_add_new_bike_part():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        user = session.query(User).filter_by(email=login_session['email']).one()
        new_bike_part = BikePart(
            name=request.form['name'],
            description=request.form['description'],
            bike_type_id=request.form['bike_type_id'],
            user_id=user.id)
        session.add(new_bike_part)
        session.commit()
        return redirect(url_for('show_bikes'))
    else:
        bike_types = session.query(BikeType).all()
        return render_template('add_new_bike_part.html', bike_types=bike_types)


@app.route('/catalog/<string:bike_part_id>/<string:bike_part_name>/edit', methods=['GET', 'POST'])
def show_edit_bike_part(bike_part_id, bike_part_name):
    if 'username' not in login_session:
        return redirect('/login')
    bike_part = session.query(BikePart).filter_by(id=bike_part_id).one()
    if bike_part.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to edit this bike part. Please add your own bike part in order to edit.');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        bike_part.name = request.form['name']
        bike_part.description = request.form['description']
        bike_part.bike_type_id = request.form['bike_type_id']
        session.add(bike_part)
        session.commit()
        return redirect(url_for('show_bikes'))
    else:
        bike_types = session.query(BikeType).all()
        return render_template('edit_bike_part.html', bike_types=bike_types, bike_part=bike_part)


@app.route('/catalog/<string:bike_part_id>/<string:bike_part_name>/delete', methods=['GET', 'POST'])
def delete_bike_part(bike_part_id, bike_part_name):
    if 'username' not in login_session:
        return redirect('/login')
    bike_part = session.query(BikePart).filter_by(id=bike_part_id).one()
    if bike_part.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to edit this bike part. Please add your own bike part in order to edit.');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        session.delete(bike_part)
        session.commit()
        return redirect(url_for('show_bikes'))
    else:
        return render_template('delete_bike_part.html')


@app.route('/bike_types/json')
def bike_types_json():
    bike_types = session.query(BikeType).all()
    return jsonify(bike_types=[bike_type.serialize for bike_type in bike_types])


@app.route('/bike_parts/json')
def bike_parts_json():
    bike_parts = session.query(BikePart).all()
    return jsonify(bike_parts=[bike_part.serialize for bike_part in bike_parts])


def create_user(login_session):
    newUser = User(name=login_session['username'], email=login_session[
        'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def get_user_info(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def get_user_id(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)

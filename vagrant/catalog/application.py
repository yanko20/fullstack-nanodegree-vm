from flask import Flask, render_template
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, BikeType, BikePart, User

app = Flask(__name__)
engine = create_engine('sqlite:///bikeparts.db?check_same_thread=False')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
@app.route('/catalog')
def show_bikes():
    bike_types = session.query(BikeType).all()
    bike_parts = session.query(BikePart).order_by(BikePart.id.desc()).limit(9)
    return render_template('index.html', bike_types=bike_types, bike_parts=bike_parts)


# Show a restaurant menu
@app.route('/catalog/<string:bike_type_name>/items')
def show_bike_items(bike_type_name):
    bike_types = session.query(BikeType).all()
    bike_type = session.query(BikeType).filter_by(name=bike_type_name).one()
    bike_parts = session.query(BikePart).filter_by(
        bike_type_id=bike_type.id).all()
    bike_part_count = len(bike_parts)
    return render_template('bike_items.html',
                           bike_types=bike_types,
                           bike_parts=bike_parts,
                           bike_type=bike_type,
                           bike_part_count=bike_part_count)


@app.route('/catalog/<string:bike_type_name>/<string:bike_part_name>')
def show_bike_part_description(bike_type_name, bike_part_name):
    bike_type_id = session.query(BikeType).filter_by(name=bike_type_name).one().id
    bike_part_description = session.query(BikePart).filter_by(name=bike_part_name,
                                                              bike_type_id=bike_type_id).one().description
    return render_template('bike_part_description.html',
                           bike_type_name=bike_type_name,
                           bike_part_description=bike_part_description)


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
    app.debug = True
    app.run(host='0.0.0.0', port=8000)

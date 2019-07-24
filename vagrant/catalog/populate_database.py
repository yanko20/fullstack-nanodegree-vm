from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, BikeType, BikePart, User

engine = create_engine('sqlite:///bikeparts.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

session.query(User).delete()
session.query(BikeType).delete()
session.query(BikePart).delete()
session.commit()

# Create dummy user
User1 = User(name="Robo Barista", email="tinnyTim@udacity.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()

road_bike = BikeType(user_id=1, name='Road')
mountain_bike = BikeType(user_id=1, name='Mountain')
hybrid_bike = BikeType(user_id=1, name='Hybrid')

road_bike_frame = BikePart(user_id=1, name='Frame', bike_type=road_bike, description='Road bike frame description.')
mountain_bike_frame = BikePart(user_id=1, name='Frame', bike_type=mountain_bike, description='Mountain bike frame description.')
hybrid_bike_frame = BikePart(user_id=1, name='Frame', bike_type=hybrid_bike, description='Hybrid bike frame description.')

road_bike_handlebar = BikePart(user_id=1, name='Handlebar', bike_type=road_bike, description='Road bike handlebar description.')
mountain_bike_handlebar = BikePart(user_id=1, name='Handlebar', bike_type=mountain_bike,
                                   description='Mountain bike handlebar description.')
hybrid_bike_handlebar = BikePart(user_id=1, name='Handlebar', bike_type=hybrid_bike,
                                 description='Hybrid bike handlebar description.')

session.add(road_bike)
session.add(mountain_bike)
session.add(hybrid_bike)

session.add(road_bike_frame)
session.add(mountain_bike_frame)
session.add(hybrid_bike_frame)

session.add(road_bike_handlebar)
session.add(mountain_bike_handlebar)
session.add(hybrid_bike_handlebar)

session.commit()

print('added bike types!')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, BikeType, BikePart

engine = create_engine('sqlite:///bikeparts.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

session.query(BikeType).delete()
session.query(BikePart).delete()
session.commit()

road_bike = BikeType(name='Road')
mountain_bike = BikeType(name='Mountain')
hybrid_bike = BikeType(name='Hybrid')

road_bike_frame = BikePart(name='Frame', bike_type=road_bike, description='Road bike frame description.')
mountain_bike_frame = BikePart(name='Frame', bike_type=mountain_bike, description='Mountain bike frame description.')
hybrid_bike_frame = BikePart(name='Frame', bike_type=hybrid_bike, description='Hybrid bike frame description.')

road_bike_handlebar = BikePart(name='Handlebar', bike_type=road_bike, description='Road bike handlebar description.')
mountain_bike_handlebar = BikePart(name='Handlebar', bike_type=mountain_bike,
                                   description='Mountain bike handlebar description.')
hybrid_bike_handlebar = BikePart(name='Handlebar', bike_type=hybrid_bike,
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

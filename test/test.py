from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine("mysql+pymysql://dev:12345678@localhost/search_engine")
session = sessionmaker(bind=engine)
print(engine)
print(session)
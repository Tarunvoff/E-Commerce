from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
#from psycopg2 import 

username = "postgres"
password = 12345
ip_address = "localhost"
port = 5432
database = "intern"

db_string = f"postgresql://{username}:{password}@{ip_address}:{port}/{database}"



engine = create_engine(db_string)



Base=declarative_base()
sessionlocal=scoped_session(sessionmaker(bind=engine))

def get_db() :
    Session=sessionmaker(bind=engine)
    session=Session()
    session.autoflush=False
    try :
        yield session
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from configuration import config

#from psycopg2 import 
# db_config = config["database"]
print(config.app_config)
if 'database' in config.app_config:
    db_config = config.app_config['database']
    if 'username' in db_config:
        username = db_config['username']
    else:
        raise KeyError("'username' key is missing in 'database' configuration")
else:
    raise KeyError("'database' key is missing in configuration")
db_config = config.app_config["database"]
username = db_config["username"]
password = db_config["password"]
ip_address= db_config["host"]
port = db_config["port"]
database = db_config["database"]

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
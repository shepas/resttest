from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:////tmp/test.db', convert_unicode=True, echo=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         expire_on_commit=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    ''' Инициализация бд и предварительное заполнение справочников '''
    import models
    Base.metadata.create_all(bind=engine)

    for v in ['Unpaid', 'Paid', 'Active', 'Deleted']:
        status = models.RbStatus(v)
        db_session.add(status)

    for v in [10, 20]:
        size = models.RbSize(v)
        db_session.add(size)

    db_session.commit()
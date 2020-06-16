# *** !!! This is not a final solution. This class needs a lot of improvements. !!! ***
"""
: This class is a helper class the check the status of the task(convertion) begin processed by Celery Worker.
"""
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine


Base = automap_base()
# : Map to the existing db: data.db
engine = create_engine('sqlite:///data.db')
# Reflect or get tables from data.db
Base.prepare(engine, reflect=True)

# !!! : Map to celery_taskmeta table
Tasks = Base.classes.celery_taskmeta

# !!! : Create session to perform queries
session = Session(engine)

"""
: This is a helper function to check the status of the task.
: This function returns the first row(result) of the query.
"""
def get_status(_id_):
    return session.query(Tasks).filter_by(task_id = _id_).first()


def find_by_id(_id_):
    return session.query(Tasks).filter_by(id = _id_).first()
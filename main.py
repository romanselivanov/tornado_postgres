
from tornado.options import define, options
from tornado import ioloop, web
from routers.views import (
    AddBodyView, GetBodyView, RemoveBodyView, UpdateBodyView, GetApiStatisticView
)
from crud.database import db, Base, db_engine, db_session

define(
    "port", default=8000,
    help="Port for webserver to run"
)
define(
    "executor_max_threads",
    default=20,
    help="max threads for threadpool executor"
)


class MainApplication(web.Application):
    """ Storing some sqlalchemy session information in the application """
    def __init__(self, *args, **kwargs):
        """ setup the session to engine linkage in the initialization """
        self.session = kwargs.pop('session')
        self.session.configure(bind=db_engine)
        super(MainApplication, self).__init__(*args, **kwargs)

    def create_database(self):
        """ this will create a database """
        Base.metadata.create_all(db_engine)


application = MainApplication([
    (r"/api/add/?", AddBodyView),
    (r"/api/get/?", GetBodyView),
    (r"/api/remove/(.*?)", RemoveBodyView),
    (r"/api/update/(.*?)", UpdateBodyView),
    (r"/api/statistic/?", GetApiStatisticView),
], db=db, session=db_session)


if __name__ == "__main__":
    application.create_database()
    application.listen(options.port)
    ioloop.IOLoop.instance().start()


from tornado.options import define, options
from tornado import ioloop, web
from routers.views import (
    AddBodyView, GetBodyView, RemoveBodyView, UpdateBodyView, GetApiStatisticView
)
from crud.database import db, Base, db_engine
from tornado_swagger.setup import setup_swagger

define(
    "port", default=8000,
    help="Port for webserver to run"
)
define(
    "executor_max_threads",
    default=20,
    help="max threads for threadpool executor"
)


class Application(web.Application):
    _routes = [
        web.url(r"/api/add", AddBodyView),
        web.url(r"/api/get", GetBodyView),
        web.url(r"/api/remove/(.*?)", RemoveBodyView),
        web.url(r"/api/update/(.*?)", UpdateBodyView),
        web.url(r"/api/statistic", GetApiStatisticView),
    ]

    def __init__(self, *args, **kwargs):
        setup_swagger(
            self._routes,
            swagger_url="/doc",
            api_base_url="/",
            description="",
            api_version="1.0.0",
            title="Demo API",
            contact="admin@mail.ru",
            schemes=["http"],
        )
        super(Application, self).__init__(self._routes, *args, **kwargs)

    def create_database(self):
        """ this will create a database """
        Base.metadata.create_all(db_engine)


application = Application(db=db)

if __name__ == "__main__":
    application.create_database()
    application.listen(options.port)
    ioloop.IOLoop.instance().start()

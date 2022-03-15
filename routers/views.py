from tornado.web import RequestHandler
from tornado_sqlalchemy import SessionMixin, as_future
from crud.models import RequestBody
from tornado import escape
import base64


class AddBodyView(SessionMixin, RequestHandler):
    
    def set_default_headers(self):
        self.set_header("Content-Type", 'application/json; charset="utf-8"')

    async def post(self):
        body = escape.json_decode(self.request.body)
        key = ''.join(k + value for k,value in body.items()).encode('ascii')
        key = base64.b64encode(key).decode("utf-8")
        with self.make_session() as session:
            obj = await as_future(
                session.query(RequestBody).filter(RequestBody.key==key).first
            )
            if obj:
                obj.request_count = obj.request_count + 1
                session.add(obj)
                session.commit()
                return self.write(key)

            new_obj = RequestBody(body=body, key=key, request_count=1) 
            session.add(new_obj)
            session.commit()

            return self.write(key)


class GetBodyView(SessionMixin, RequestHandler):

    def set_default_headers(self):
        self.set_header("Content-Type", 'application/json; charset="utf-8"')

    async def get(self):
        param = self.get_argument('key')
        
        key = bytes(param, 'ascii').decode('ascii')
        with self.make_session() as session:
            obj = await as_future(
                session.query(RequestBody).filter(RequestBody.key==key).first
            )
            if not obj:
                return self.write('Request with specified key does not exist')
            
            response = {'body': obj.body, 'duplicates': obj.request_count}
            return self.write(response)


class RemoveBodyView(SessionMixin, RequestHandler):

    def set_default_headers(self):
        self.set_header("Content-Type", 'application/json; charset="utf-8"')

    async def delete(self, id):
        id = id.split('/')[0]
        with self.make_session() as session:
            obj = await as_future(
                session.query(RequestBody).filter(RequestBody.key==id).delete
            )
            if not obj:
                return self.write('Request with specified key does not exist')

            return self.write('{} object was deleted'.format(obj))


class UpdateBodyView(SessionMixin, RequestHandler):

    def set_default_headers(self):
        self.set_header("Content-Type", 'application/json; charset="utf-8"')

    async def put(self, id):
        id = id.split('/')[0]
        with self.make_session() as session:
            obj = await as_future(
                session.query(RequestBody).filter(RequestBody.key==id).first
            )
            if not obj:
                return self.write('Request with specified key does not exist')

            body = escape.json_decode(self.request.body)
            key = ''.join(k + value for k,value in body.items()).encode('ascii')
            obj.request_count = 1
            obj.body = body
            obj.key = base64.b64encode(key).decode("utf-8")
            session.add(obj)
            session.commit()
            return self.write(obj.key)


class GetApiStatisticView(SessionMixin, RequestHandler):

    def set_default_headers(self):
        self.set_header("Content-Type", 'application/json; charset="utf-8"')

    async def get(self):
        with self.make_session() as session:
            count_all = await as_future(session.query(RequestBody).count)
            count_duplicates = await as_future(
                session.query(RequestBody).filter(RequestBody.request_count>1).count
            )
            percents = (count_duplicates / count_all) * 100
            return self.write("{}% duplicates".format(round(percents, 3))) 

from tornado.web import RequestHandler
from tornado_sqlalchemy import SessionMixin, as_future
from crud.models import RequestBody
from tornado import escape
import base64
from tornado_swagger.model import register_swagger_model
from tornado_swagger.parameter import register_swagger_parameter

@register_swagger_model
class PostRequest:
    """
    ---
    type: object
    """

@register_swagger_model
class PostResponse:
    """
    ---
    type: string
    """

class AddBodyView(SessionMixin, RequestHandler):
    
    def set_default_headers(self):
        self.set_header("Content-Type", 'application/json; charset="utf-8"')

    async def post(self):
        """
        ---
        tags:
        - Api
        description: send requests body
        summary: Add request with json body
        produces:
        - application/json
        parameters:
        -   in: body
            name: body
            description: Accept random json in body
            required: true
            schema:
                $ref: '#/definitions/PostRequest'
        responses:
            200:
                description: request key
                schema:
                    $ref: '#/definitions/PostResponse'
        """

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


@register_swagger_parameter
class KeyId:
    """
    ---
    name: key
    in: path
    description: Request body key
    required: true
    type: string
    """


@register_swagger_model
class RequestModel:
    """
    ---
    type: object
    properties:
        body:
            type: object
            properties:
                body:
                    type: string
                key:
                    type: string
        duplicates:
            type: integer
            format: int64
    """


class GetBodyView(SessionMixin, RequestHandler):

    def set_default_headers(self):
        self.set_header("Content-Type", 'application/json; charset="utf-8"')

    async def get(self):
        """
        ---
        tags:
        - Api
        summary: Get requests by key
        produces:
        - application/json
        parameters:
        -   $ref: '#/parameters/KeyId'
        responses:
            200:
              description: list of posts
              schema:
                $ref: '#/definitions/RequestModel'
        """
        param = self.get_argument('key')
        
        key = bytes(param, 'ascii').decode('ascii')
        with self.make_session() as session:
            obj = await as_future(
                session.query(RequestBody).filter(RequestBody.key==key).first
            )
            if not obj:
                return self.write(
                    {'error':'Request with specified key does not exist'}
                )
            
            response = {'body': obj.body, 'duplicates': obj.request_count}
            return self.write(response)


@register_swagger_model
class DeleteResponse:
    """
    ---
    type: object
    properties:
        Object was deleted:
            type: integer
    """


class RemoveBodyView(SessionMixin, RequestHandler):

    def set_default_headers(self):
        self.set_header("Content-Type", 'application/json; charset="utf-8"')

    async def delete(self, id):
        """
        ---
        tags:
        - Api
        summary: Delete request by key
        description: Remove request by key
        produces:
        - application/json
        parameters:
        -   $ref: '#/parameters/KeyId'
        responses:
            200:
                description: request key
                schema:
                    $ref: '#/definitions/DeleteResponse'
        """
        id = id.split('/')[0]
        with self.make_session() as session:
            obj = await as_future(
                session.query(RequestBody).filter(RequestBody.key==id).delete
            )
            if not obj:
                return self.write(
                    {'error':'Request with specified key does not exist'}
                )

            return self.write({'Object was deleted': obj})


class UpdateBodyView(SessionMixin, RequestHandler):

    def set_default_headers(self):
        self.set_header("Content-Type", 'application/json; charset="utf-8"')

    async def put(self, id):
        """
        ---
        tags:
        - Api
        description: Change request by key
        summary: Change request by key
        produces:
        - application/json
        parameters:
        -   in: body
            name: body
            description: Accept random json in body
            required: true
            schema:
                $ref: '#/definitions/PostRequest'
        responses:
            200:
                description: request key
                schema:
                    $ref: '#/definitions/PostResponse'
        """
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


@register_swagger_model
class StatisticResponse:
    """
    ---
    type: object
    properties:
        duplicates percent:
            type: string
    """


class GetApiStatisticView(SessionMixin, RequestHandler):

    def set_default_headers(self):
        self.set_header("Content-Type", 'application/json; charset="utf-8"')

    async def get(self):
        """
        ---
        tags:
        - Api
        summary: Get duplicates statistics
        produces:
        - application/json
        responses:
            200:
              description: list of posts
              schema:
                $ref: '#/definitions/StatisticResponse'
        """
        with self.make_session() as session:
            count_all = await as_future(session.query(RequestBody).count)
            count_duplicates = await as_future(
                session.query(RequestBody).filter(RequestBody.request_count>1).count
            )
            percents = (count_duplicates / count_all) * 100
            return self.write(
                {"Duplicates percent": "{}%".format(round(percents, 3))}
            )

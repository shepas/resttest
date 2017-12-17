import random
import time
from datetime import timedelta, datetime

from celery import Celery
from flask import Flask, request, jsonify
from sqlalchemy import func

from database import db_session
from models import Server, RbSize, Rack, RbStatus
from utils import getMessage, forceDateTime

app = Flask(__name__)
flask_app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)
celery.conf.update(CELERYBEAT_SCHEDULE={
    'add-every-60-seconds': {
        'task': 'checkServers',
        'schedule': timedelta(seconds=60)
    },
})

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.expunge_all()
    db_session.remove()

@app.route('/', methods=['GET'])
def getFullList():
    '''
    Список стоек и серверов в них
    :return:
    '''

    result = {'racks': []}
    for rack in Rack.query.all():
        serRack = rack.serialize()
        serRack['servers'] = []
        for server in Server.query.filter(Server.rack_id == rack.id):
            serRack['servers'].append(server.serialize())
        result['racks'].append(serRack)
    return jsonify(result)


@app.route('/server', methods=['GET'])
def getServers():
    '''
    Список серверов
    :return:
    '''

    result = {'servers': []}
    servers = Server.query.all()
    for server in servers:
        result['servers'].append(server.serialize())
    return jsonify(result)

@app.route('/server/<int:id>', methods=['GET'])
def getServerById(id):
    '''
    Информация о сервере
    :param id: Id сервера
    :return:
    '''

    server = Server.query.filter(Server.id == id)
    if server:
        return jsonify(server.serialize())
    else:
        return getMessage('Error: server with id %s not found' % id)

@app.route('/server', methods=['POST'])
def addServer():
    '''
    Добавление сервера
    :return:
    '''

    try:
        db_session.add(Server())
        db_session.commit()
        return getMessage('Server created.')
    except:
        return getMessage('Error creation of server.')

@app.route('/server/<int:id>', methods=['DELETE'])
def deleteServer(id):
    '''
    Удаление сервера
    :return:
    '''

    server = Server.query.filter(Server.id == id).first()
    if server:
        if not server.getStatus() in ['Deleted', 'Without status']:
            return getMessage('Error: server must be in status "Deleted" or "Without status"')
        else:
            try:
                db_session.delete(server)
                db_session.commit()
                return getMessage('Server deleted')
            except:
                return getMessage('Error deleting server')
    else:
        return getMessage('Error: server with id %s not found' % id)

@app.route('/rack',  methods=['GET'])
def getRacks():
    '''
    Список стоек
    :return:
    '''

    result = {'racks': []}
    for server in Rack.query.all():
        result['racks'].append(server.serialize())
    return jsonify(result)

@app.route('/rack/<int:id>', methods=['GET'])
def getRackById(id):
    '''
    Информация о скойке
    :param id: Id стойки
    :return:
    '''

    rack = Rack.query.filter(Rack.id == id).first()
    if rack:
        return jsonify(rack.serialize())
    else:
        return getMessage('Error: rack with id %s not found' % id)

@app.route('/rack', methods=['POST'])
def addRack():
    '''
    Добавление стойки
    :return:
    '''

    if not request.json or not request.json['size']:
        return jsonify({'message': 'Error: need size'})

    size_id = RbSize.query.filter(RbSize.value == request.json['size']).first().id
    if size_id:
        try:
            db_session.add(Rack(size_id))
            db_session.commit()
            return getMessage('Rack created.')
        except:
            return getMessage('Error creation of rack')
    else:
        return getMessage('Error: size with value %s not found' % request.json['size'])

@app.route('/rack/<int:id>', methods=['DELETE'])
def deleteRack(id):
    '''
    Удаление стойки
    :return:
    '''

    rack = Rack.query.filter(Rack.id == id)
    if rack:
        if rack.getBuzySlots():
            return getMessage('Error: rack have servers')
        else:
            try:
                db_session.delete(rack)
                return getMessage('Server deleted')
            except:
                return getMessage('Error deleting of rack')
    else:
        return getMessage('Error: rack with id %s not found' % id)

@app.route('/serveroperations', methods=['POST'])
def addServerToRack():
    '''
    Добавление сервера в стойку
    :param server_id: id of server
    :param rack_id: id of rack
    :return:
    '''

    if not request.json or not request.json['server_id'] or not request.json['rack_id']:
        return getMessage('Error: not enough arguments')

    server_id = request.json['server_id']
    rack_id = request.json['rack_id']
    server = Server.query.filter(Server.id == server_id).first()
    rack = Rack.query.filter(Rack.id == rack_id).first()

    if not server:
        return getMessage('Error: server with id %s not found' % server_id)
    elif not rack:
        return getMessage('Error: rack with id %s not found' % rack_id)
    elif not server.getStatus() in ['Unpaid', 'Deleted', 'Without status']:
        return getMessage('Error: cannot use server in status %s' % server.getStatus())
    elif server.rack_id:
        return getMessage('Error: server already in rack with id %s' % server.rack_id)
    elif rack.getSize() == rack.getBuzySlots():
        return getMessage('Error: rack is full')

    try:
        server.status_id = RbStatus.query.filter(RbStatus.value == 'Unpaid').first().id
        server.rack_id = rack.id
        server.modifyDatetime = func.now()
        rack.modifyDatetime = func.now()
        db_session.commit()
        return getMessage('Server added to rack')
    except:
        return getMessage('Error adding server to rack')


@app.route('/serveroperations', methods=['PUT'])
def changeServerStatus():
    '''
    Смена статуса сервера
    :param server_id: id of server
    :param status: value RbStatus
    :param expDate: expiration Date
    :return:
    '''
    if not request.json or not 'server_id' in request.json.keys() or not 'status' in request.json.keys():
        return getMessage('Error: not enough arguments')

    server_id = request.json['server_id']
    status = request.json['status']
    server = Server.query.filter(Server.id == server_id).first()
    status_id = RbStatus.query.filter(RbStatus.value == status).first().id
    if not server:
        return getMessage('Error: server with id %s not found' % server_id)
    elif not status_id:
        return getMessage('Error: status with value %s not found' % status)
    elif server.getStatus() == 'Deleted':
        return getMessage('Error: server in status "Deleted"')
    elif not server.rack_id:
        return getMessage('Error: server not in rack')
    elif status == 'Paid' and not 'expDate' in request.json.keys():
        return getMessage('For this status need expirationDate')
    elif not server.getStatus() == 'Unpaid':
        return getMessage('Error: cannot change to this status from %s' % server.getStatus())

    if server.getStatus() == 'Unpaid':
        server.status_id = status_id
        server.expirationDate = forceDateTime(request.json['expDate'])
        server.modifyDatetime = func.now()
        db_session.commit()
        activateServer.delay(server.id)
        return getMessage('Status change to "Paid"')
    elif status == 'Deleted':
        server.status_id = status_id
        server.expirationDate = None
        server.modifyDatetime = func.now()
        db_session.commit()
        return getMessage('Status change to "Deleted"')


@app.route('/serveroperations/<int:id>', methods=['DELETE'])
def deleteServerFromRack(id):
    '''
    Удаление сервера из стойки
    :param: id of server
    :return:
    '''

    server = Server.query.filter(Server.id == id).first()
    if not server:
        return getMessage('Error: server with id %s not found' % id)
    elif not server.getStatus() in ['Unpaid', 'Deleted', 'Without status']:
        return getMessage('Error: cannot use server in status %s' % server.getStatus())

    try:
        server.rack_id = None
        db_session.commit()
        return getMessage('Server deleted from rack')
    except:
        return getMessage('Error deleting server from rack')


@app.route('/refbooks', methods=['GET'])
def getRefBooks():
    '''
    Справочники
    :return:
    '''

    result = {'sizes': [], 'statuses': []}
    for size in RbSize.query.all():
        result['sizes'].append(size.serialize())
    for status in RbStatus.query.all():
        result['statuses'].append(status.serialize())
    return result

@celery.task(name='activate_server')
def activateServer(srv_id):
    time.sleep(random.randint(10, 20))
    srv = db_session.query(Server).filter(Server.id == srv_id).first()
    srv.status_id = RbStatus.query.filter(RbStatus.value == 'Active').first().id
    db_session.commit()

@celery.task(name='checkServers')
def checkServers():
    for server in Server.query.all():
        if server.getStatus() == 'Active' and server.expirationDate < datetime.now():
            server.status_id = RbStatus.query.filter(RbStatus.value == 'Unpaid').first().id
            server.expirationDate = None
            db_session.commit()

if __name__ == '__main__':
    app.run(debug=True, port=8080)
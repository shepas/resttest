from flask import Flask, request, jsonify
from sqlalchemy import func

from database import db_session
from models import Server, RbSize, Rack, RbStatus

app = Flask(__name__)

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

@app.route('/', methods=['GET'])
def getFullList():
    '''
    Список стоек и серверов в них
    :return:
    '''
    pass

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
        return jsonify({'message': 'Error: server with id %s not found' % id})

@app.route('/server', methods=['POST'])
def addServer():
    '''
    Добавление сервера
    :return:
    '''

    try:
        db_session.add(Server())
        db_session.commit()
        return jsonify({'message': 'Server created.'})
    except:
        return jsonify({'message': 'Error creation of server.'})

@app.route('/server/<int:id>', methods=['DELETE'])
def deleteServer(id):
    '''
    Удаление сервера
    :return:
    '''

    server = Server.query.filter(Server.id == id).first()
    if server:
        if not server.getStatus() in ['Deleted', 'Without status']:
            return jsonify({'message': 'Error: server must be in status "Deleted" or "Without status"'})
        else:
            try:
                db_session.delete(server)
                db_session.commit()
                return jsonify({'message': 'Server deleted'})
            except:
                return jsonify({'message': 'Error deleting server'})
    else:
        return jsonify({'message': 'Error: server with id %s not found' % id})

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
        return jsonify({'message': 'Error: rack with id %s not found' % id})

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
            return jsonify({'message': 'Rack created.'})
        except:
            return jsonify({'message': 'Error creation of rack'})
    else:
        return jsonify({'message': 'Error: size with value %s not found' % request.json['size']})

@app.route('/rack/<int:id>', methods=['DELETE'])
def deleteRack(id):
    '''
    Удаление стойки
    :return:
    '''

    rack = Rack.query.filter(Rack.id == id)
    if rack:
        if rack.getBuzySlots():
            return jsonify({'message': 'Error: rack have servers'})
        else:
            try:
                db_session.delete(rack)
                return jsonify({'message': 'Server deleted'})
            except:
                return jsonify({'message': 'Error deleting of rack'})
    else:
        return jsonify({'message': 'Error: rack with id %s not found' % id})

@app.route('/serveroperations', methods=['POST'])
def addServerToRack():
    '''
    Добавление сервера в стойку
    :param server_id: id of server
    :param rack_id: id of rack
    :return:
    '''

    if not request.json or not request.json['server_id'] or not request.json['rack_id']:
        return jsonify({'message': 'Error: not enough arguments'})

    server_id = request.json['server_id']
    rack_id = request.json['rack_id']
    server = Server.query.filter(Server.id == server_id).first()
    rack = Rack.query.filter(Rack.id == rack_id).first()

    if not server:
        return jsonify({'message': 'Error: server with id %s not found' % server_id})
    elif not rack:
        return jsonify({'message': 'Error: rack with id %s not found' % rack_id})
    elif not server.getStatus() in ['Unpaid', 'Deleted', 'Without status']:
        return jsonify({'message': 'Error: cannot use server in status %s' % server.getStatus()})
    elif server.rack_id:
        return jsonify({'message': 'Error: server already in rack with id %s' % server.rack_id})
    elif rack.getSize() == rack.getBuzySlots():
        return jsonify({'message': 'Error: rack is full'})

    try:
        server.status_id = RbStatus.query.filter(RbStatus.value == 'Unpaid').first().id
        server.rack_id = rack.id
        server.modifyDatetime = func.now()
        rack.modifyDatetime = func.now()
        db_session.commit()
        return jsonify({'message': 'Server added to rack'})
    except:
        return jsonify({'message': 'Error adding server to rack'})


@app.route('/serveroperations', methods=['PUT'])
def changeServerStatus():
    '''
    Смена статуса сервера
    :param server_id: id of server
    :param status: value RbStatus
    :param expDate: expiration Date
    :return:
    '''
    if not request.json or not request.json['server_id'] or not request.json['status']:
        return jsonify({'message': 'Error: not enough arguments'})

    server_id = request.json['server_id']
    status = request.json['status']
    server = Server.query.filter(Server.id == server_id).first()
    status_id = RbStatus.query.filter(RbStatus.value == status).first()

    if not server:
        return jsonify({'message': 'Error: server with id %s not found' % server_id})
    elif not status_id:
        return jsonify({'messsage': 'Error: status with value %s not found' % status})
    elif server.getStatus() == 'Deleted':
        return jsonify({'message': 'Error: server in status "Deleted"'})
    elif not server.rack_id:
        return jsonify({'message': 'Error: server not in rack'})
    elif server == 'Paid' and not request.json['expDate']:
        return jsonify({'message': 'For this status need expirationDate'})
    elif not server.getStatus() == 'Unpaid':
        return jsonify({'message': 'Error: cannot change to this status from %s' % server.getStatus()})

    if server.getStatus() == 'Unpaid':
        server.status_id = status_id
        server.expirationDate = request.json['expDate']
        server.modifyDatetime = func.now()
        db_session.commit()
        return jsonify({'message': 'Status change to "Paid"'})
    elif status == 'Deleted':
        server.status_id = status_id
        server.expirationDate = None
        server.modifyDatetime = func.now()
        db_session.commit()
        return jsonify({'message': 'Status change to "Deleted"'})


@app.route('/serveroperations/<int:id>', methods=['DELETE'])
def deleteServerFromRack(id):
    '''
    Удаление сервера из стойки
    :param: id of server
    :return:
    '''

    server = Server.query.filter(Server.id == id).first()
    if not server:
        return jsonify({'message': 'Error: server with id %s not found' % id})
    elif not server.getStatus() in ['Unpaid', 'Deleted', 'Without status']:
        return jsonify({'message': 'Error: cannot use server in status %s' % server.getStatus()})

    try:
        server.rack_id = None
        db_session.commit()
        return jsonify({'message': 'Server deleted from rack'})
    except:
        return jsonify({'message': 'Error deleting server from rack'})


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

if __name__ == '__main__':
    app.run(debug=True, port=8080)
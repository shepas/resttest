from flask import Flask, request, jsonify
from database import db_session
from models import Server, RbSize, Rack

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
    :return:
    '''
    pass

@app.route('/serveroperations', methods=['PUT'])
def changeServerStatus():
    '''
    Смена статуса сервера
    :return:
    '''
    pass

@app.route('/serveroperations', methods=['DELETE'])
def deleteServerFromRack():
    '''
    Удаление сервера из стойки
    :return:
    '''

if __name__ == '__main__':
    app.run(debug=True, port=8080)
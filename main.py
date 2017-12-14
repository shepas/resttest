from flask import Flask, request, jsonify
from database import db_session

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

@app.route('/', method=['GET'])
def getFullList():
    '''
    Список стоек и серверов в них
    :return:
    '''
    pass

@app.route('/server', method=['GET'])
def getServers():
    '''
    Список серверов
    :return:
    '''
    pass

@app.route('server/<integer:id>', method=['GET'])
def getServerById(id):
    '''
    Информация о сервере
    :param id: Id сервера
    :return:
    '''
    pass

@app.route('/server', method=['POST'])
def addServer():
    '''
    Добавление сервера
    :return:
    '''
    pass

@app.route('/server', method=['PUT'])
def updateSever():
    '''
    Изменение сервера
    :return:
    '''
    pass

@app.route('/server', method=['DELETE'])
def deleteServer():
    '''
    Удаление сервера
    :return:
    '''

@app.route('/rack',  method=['GET'])
def getRacks():
    '''
    Список стоек
    :return:
    '''
    pass

@app.route('rack/<integer:id>', method=['GET'])
def getRackById(id):
    '''
    Информация о скойке
    :param id: Id стойки
    :return:
    '''
    pass

@app.route('/rack', method=['POST'])
def addRack():
    '''
    Добавление стойки
    :return:
    '''
    pass

@app.route('/rack', method=['DELETE'])
def deleteRack():
    '''
    Удаление стойки
    :return:
    '''

@app.route('/serveroperations', method=['POST'])
def addServerToRack():
    '''
    Добавление сервера в стойку
    :return:
    '''
    pass

@app.route('/serveroperations', method=['PUT'])
def changeServerStatus():
    '''
    Смена статуса сервера
    :return:
    '''
    pass

@app.route('/serveroperations', method=['DELETE'])
def deleteServerFromRack():
    '''
    Удаление сервера из стойки
    :return:
    '''

if __name__ == '__main__':
    app.run(debug=True, port=8080)
import unittest
import requests
import json
import sys

class TestFlaskApiUsingRequests(unittest.TestCase):
    # Создание сервера
    def test_create_server(self):
        response = requests.post('http://localhost:8080/server', json={})
        self.assertEqual(response.json(), {'message': 'Server created.'})

    # Создание стойки
    def test_create_rack(self):
        response = requests.post('http://localhost:8080/rack', json={"size": 10})
        self.assertEqual(response.json(), {'message': 'Rack created.'})

    # Попытка создать стойку с неверным размером
    def test_wrongsize_rack(self):
        response = requests.post('http://localhost:8080/rack', json={"size": 19})
        self.assertEqual(response.json(), {'message': 'Error: size with value 19 not found'})

    # Добавление сервера в стойку
    def test_addServerToRack(self):
        requests.post('http://localhost:8080/server', json={})
        response = requests.post('http://localhost:8080/serveroperations', json={"server_id": 2, "rack_id": 1})
        self.assertEqual(response.json(), {'message': 'Server added to rack'})

    # Проверка статуса добавленного сервера
    def test_ServerStatus(self):
        response = requests.get('http://localhost:8080/server/2')
        dict = response.json()
        self.assertEqual('Unpaid', dict['status'])

if __name__ == "__main__":
    unittest.main()
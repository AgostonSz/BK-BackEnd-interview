from fastapi.testclient import TestClient
from main import app
client = TestClient(app)

def test_create_item1():
    files = [('files', open('img1.jpg', 'rb')), ('files', open('img2.jpg', 'rb'))]
    payload = {"title": "Title", "message": "Message"}
    response = client.post("/posts/", params=payload, files=files)
    assert response.status_code == 200
    assert response.json()['title'] == 'Title'
    assert response.json()['message'] == 'Message'
    assert response.json()['date_creation'] == response.json()['date_last_change']
    assert response.json()['email']
    assert len(response.json()['images']) == 2
    print('Testcase post1 passed')
    return response.json()['_id']

def test_create_item2():
    payload = {"title": "Title", "message": "Message"}
    response = client.post("/posts/", params=payload)
    assert response.status_code == 200
    assert response.json()['title'] == 'Title'
    assert response.json()['message'] == 'Message'
    assert response.json()['date_creation'] == response.json()['date_last_change']
    assert response.json()['email']
    assert len(response.json()['images']) == 0
    print('Testcase post2 passed')
    return response.json()['_id']

def test_read_item(id):
    response = client.get(f"/posts/{id}")
    assert response.status_code == 200
    assert response.json()['title']
    assert response.json()['message']
    assert response.json()['email']
    print('Testcase read passed')

def test_delete_item(id):
    response = client.delete(f"/posts/{id}")
    assert response.status_code == 200
    print('Testcase delete passed')

def test_update_item(id):
    files = [('files', open('img1.jpg', 'rb'))]
    payload = {"title": "NewTitle", "message": "NewMessage"}
    response = client.put(f"/posts/{id}", params=payload, files=files)
    assert response.status_code == 200
    assert response.json()['title'] == 'NewTitle'
    assert response.json()['message'] == 'NewMessage'
    assert response.json()['date_creation'] != response.json()['date_last_change']
    assert response.json()['email']
    assert len(response.json()['images']) == 1
    print('Testcase update passed')


id1 = test_create_item1()
id2 = test_create_item2()
test_read_item(id1)
test_update_item(id1)
test_delete_item(id1)
test_delete_item(id2)
print('------------------All tests passed-------------------')
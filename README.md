# BK-BackEnd-interview
 
## Telepítés
```
pip install -r requirements.txt
```

Python verzió: 3.8.10

Lokálisan futó MongoDB szerver szükséges a működéshez 

## Futtatás:
```
python main.py
```
Elindítja a szervert a következő endpointokkal:

* Create: /posts
* Read: /posts vagy /posts/id
* Update: /posts/id
* Delete /posts/id

Első alkalommal google fiókkal történő authentikáció szükséges, a token a ```token.json``` fileba kerül elmentésre, és később onnan automatikusan authentikálja a felhasználót.

## Tesztek:
```
python tests.py
```
A következő teszteket futtatja:
* Create
* Read
* Update
* Delete

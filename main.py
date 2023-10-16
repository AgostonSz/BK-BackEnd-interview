# Import the necessary modules
from fastapi import FastAPI, Depends, File, UploadFile, HTTPException
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse
from datetime import datetime
from pydantic import BaseModel
import uvicorn
from pymongo import MongoClient
import gridfs
from typing import List
from bson.objectid import ObjectId
from authentication import authenticate


# Create a new instance of the FastAPI class
app = FastAPI()

# MongoDB
client = MongoClient(f"mongodb://admin:password@mongo:27017/")
db = client['database']
collection = db['posts']

result = collection.insert_one({'test': 'test'})

fs = gridfs.GridFS(db)
try:
    client.admin.command('ismaster')
    print('Connection successful!')
except Exception as e:
    print('Connection unsuccessful:', e)

IP = '0.0.0.0'
PORT = 8000


ACCEPTED_IMAGE_FILE_FORMATS = ['jpg', 'jpeg', 'png']


# Define the data model for the news post
class Post(BaseModel):
    title: str
    message: str


# Define the endpoints for CRUD operations
# Create Post
@app.post("/posts")
def create_post(post: Post = Depends(), files: List[UploadFile] = {}):
    email = authenticate()

    post = post.dict()
    post['date_creation'] = datetime.now().isoformat()
    post['date_last_change'] = post['date_creation']
    post['email'] = email
    post['images'] = {}
    
    for file in files:
        if file.filename.split('.')[1] not in ACCEPTED_IMAGE_FILE_FORMATS:
            raise HTTPException(status_code=400, detail=f'Error: Incorrect file format, only accepting {ACCEPTED_IMAGE_FILE_FORMATS}')
            return
        try:
            contents = file.file.read()
            obj_id = fs.put(contents, filename=file.filename)
            post['images'][str(obj_id)]= str(file.filename)
        except Exception:
            raise HTTPException(status_code=400, detail="Error: There was an error uploading the file")
            return
        finally:
            file.file.close()

    collection.insert_one(post)
    post['_id'] = str(post['_id']) # fixes TypeError('vars() argument must have __dict__ attribute')] with fastAPI and mongoDB    
    return post

# Return all posts
@app.get("/posts")
async def get_post_by_id():
    posts = collection.find({})
    post_ids = [str(post['_id']) for post in posts] # fixes TypeError('vars() argument must have __dict__ attribute')] with fastAPI and mongoDB
    return post_ids

# Return 1 post by id
@app.get("/posts/{post_id}")
async def get_post_by_id(post_id: str):
    post = collection.find_one({'_id': ObjectId(post_id)})
    if not post:
        raise HTTPException(status_code=404, detail='Error: Post not found')
        return
    post['_id'] = str(post['_id']) # fixes TypeError('vars() argument must have __dict__ attribute')] with fastAPI and mongoDB
    return post

# Update 1 post by id
@app.put("/posts/{post_id}")
async def update_post(post_id: str, post: Post = Depends(), files: List[UploadFile] = {}):
    post = post.dict()

    email = authenticate()
    old_post = collection.find_one({'_id': ObjectId(post_id)})
    if not old_post:
        raise HTTPException(status_code=404, detail='Error: Post not found')
    if email != old_post['email']:
        raise HTTPException(status_code=404, detail=f'Error: You can only change your own posts')

    post['email'] = email
    post['date_creation'] = old_post['date_creation']
    post['date_last_change']: datetime = datetime.now().isoformat()

    # delete images from old post based on file name, if not in updated post
    new_fnames = {file.filename for file in files}
    for fid, fname in list(old_post['images'].items()):
        if fname not in new_fnames:
            fs.delete(ObjectId(fid))  
            old_post['images'].pop(fid)

    # keep unchanged images from old post
    post['images'] = old_post['images'] 

    old_fnames = {fname for _,fname in old_post['images'].items()}
    # upload new images
    for file in files:
        if file.filename in old_fnames:
            continue
        if file.filename.split('.')[1] not in ACCEPTED_IMAGE_FILE_FORMATS:
            raise HTTPException(status_code=400, detail=f'Error: Incorrect file format, only accepting {ACCEPTED_IMAGE_FILE_FORMATS}')
        try:
            contents = file.file.read()
            obj_id = fs.put(contents, filename=file.filename)
            post['images'][str(obj_id)]= str(file.filename)
        except Exception:
            raise HTTPException(status_code=400, detail="Error: There was an error uploading the file")
            
        finally:
            file.file.close()
    
    collection.update_one({'_id': ObjectId(post_id)}, {'$set': post})
    return post

# Delete 1 post by id
@app.delete("/posts/{post_id}")
async def delete_post_by_id(post_id: str):
    email = authenticate()
    post = collection.find_one({'_id': ObjectId(post_id)})
    if not post:
        raise HTTPException(status_code=404, detail='Error: Post not found')
    if email != post['email']:
        raise HTTPException(status_code=404, detail=f'Error: You can only delete your own posts')
    # delete images from post
    for fid in post['images']:
        fs.delete(ObjectId(fid))  
    
    collection.delete_one({'_id': ObjectId(post_id)})
    post['_id'] = str(post['_id']) # fixes TypeError('vars() argument must have __dict__ attribute')] with fastAPI and mongoDB
    return post


# Generate an OpenAPI schema and Swagger UI HTML page
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="BK News API",
        version="0.1.0",
        description="This is a CRUD API for posting news.",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

@app.get("/docs", response_class=HTMLResponse)
async def get_documentation():
    return get_swagger_ui_html(openapi_url="/openapi.json", title="BK News API")

@app.get("/openapi.json")
async def get_open_api_endpoint():
    return JSONResponse(content=custom_openapi())

# Run your application using uvicorn
if __name__ == "__main__":
    uvicorn.run(app, host=IP, port=PORT)


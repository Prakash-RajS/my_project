# fastapi_app/main.py

"""import os
import sys
from fastapi import FastAPI

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(__file__)))  # add project to path
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_project.settings')  # replace with your actual Django project name

import django
django.setup()

# Now import your FastAPI routes AFTER django.setup()

from fastapi_app.auth import router as auth_router

app = FastAPI()

# Include routes
#app.include_router(auth.router)
app.include_router(auth_router, prefix="/auth", tags=["auth"])"""

# fastapi_app/main.py its work correctly in singup and login page 
"""from fastapi import FastAPI
from fastapi_app.auth import router as auth_router

app = FastAPI()

# Include your auth routes
app.include_router(auth_router)"""

#its used for icons
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from fastapi_app.auth import router as auth_router

app = FastAPI()
app.include_router(auth_router)

# Serve static HTML page
@app.get("/")
async def serve_index():
    return FileResponse(os.path.join("fastapi_app", "frontend", "index.html"))

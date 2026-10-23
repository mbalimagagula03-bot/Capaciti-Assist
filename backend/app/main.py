from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.core.config import settings
app=FastAPI(title='OpsPilot API',version='0.1.0')
app.add_middleware(CORSMiddleware,allow_origins=[settings.cors_origin],allow_methods=['GET','POST','PATCH'],allow_headers=['Authorization','Content-Type','Idempotency-Key'])
app.include_router(router)

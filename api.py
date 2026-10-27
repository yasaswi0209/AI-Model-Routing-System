"""Optional local API for integrations. No authentication: do not expose publicly."""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Literal
from core import process, ProviderError
from storage import history

app=FastAPI(title='SmartRoute API',version='1.0.0')
class Request(BaseModel):
    question: str=Field(min_length=1,max_length=12000)
    mode: Literal['auto','small','large']='auto'
    demo: bool=True
@app.get('/health')
def health(): return {'status':'ok'}
@app.post('/ask')
def ask(body: Request):
    try: return process(body.question,body.mode,body.demo)
    except ValueError as e: raise HTTPException(400,str(e))
    except ProviderError as e: raise HTTPException(502,str(e))
@app.get('/history')
def get_history(): return history()

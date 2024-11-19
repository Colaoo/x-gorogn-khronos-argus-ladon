#!encoding=utf8
import base64

import requests
from fastapi import FastAPI, Form, Response
from pydantic import BaseModel

from lib.Captcha import PuzzleSolver
from lib.TTEncrypt import TT
from lib.XGorgon import XGorgon
from lib.Xlog import XLOG
from lib.XArgus import Argus
from lib.XLadon import Ladon


class XGorgonDict(BaseModel):
    params: str
    headers: dict

class XArgusDict(BaseModel):
    params: str # Request Params
    timestamp:int # X-Khronos value from X-Gorgon
    stub:None | str # X-SS-STUB value from header


class XLadonDict(BaseModel):
    timestamp:int # X-Khronos value from X-Gorgon
    license_id:int |None # License ID : Default 1611921764
    aid: int | None # aid value from params: Default 1233


class PostBase64Dict(BaseModel):
    base64: str


app = FastAPI()


@app.post("/captcha")
def captcha(puzzle: str = Form(...), piece: str = Form(...)):
    try:
        base64puzzle = base64.b64encode(requests.get(puzzle).content)
        base64piece = base64.b64encode(requests.get(piece).content)
        solver = PuzzleSolver(base64puzzle=base64puzzle, base64piece=base64piece)
        return {"x": solver.get_position()}
    except Exception as e:
        print(e)
        return None


@app.post("/x-gorgon")
def x_gorgon(req: XGorgonDict):
    try:
        xg = XGorgon()
        # req.headers shall contain x-ss-stub (md5) of post body for post request
        # req.headers shall contain cookie as string 
        return xg.calculate(req.params, req.headers)
    except Exception as e:
        print(e)
        return None


@app.post("/tt_encrypt")
def tt_encrypt(req: PostBase64Dict):
    try:
        lib = TT()
        # req.base64 = Base64 encoded value of JSON post body stringified
        body = str(base64.b64decode(req.base64))
        data = lib.encrypt(body)
        return {"base64": base64.b64encode(data)}
    except Exception as e:
        print(e)
        return None


@app.post("/tt_decrypt")
def tt_encrypt(req: PostBase64Dict):
    try:
        ttencrypt = TT()
        # req.base64 = Base64 encoded value of ttencrypted binary post body
        body = base64.b64decode(req.base64)
        data = ttencrypt.decrypt(body)
        return Response(data, headers={"Content-Type": "application/json"})
    except Exception as e:
        return None


@app.post("/xlog_encrypt")
def tt_encrypt(req: PostBase64Dict):
    try:
        lib = XLOG()
        # req.base64 = Base64 encoded value of JSON post body stringified
        body = str(base64.b64decode(req.base64)) 
        data = lib.encrypt(body)
        return {"base64": base64.b64encode(data)}
    except Exception as e:
        print(e)
        return None


@app.post("/xlog_decrypt")
def tt_encrypt(req: PostBase64Dict):
    try:
        lib = XLOG()
        body = base64.b64decode(req.base64)
        data = lib.decrypt(body)
        return Response(data, headers={"Content-Type": "application/json"})
    except Exception as e:
        print(e)
        return None


@app.post("/xargus")
def x_argus(req: XArgusDict):
    try:
        # timestamp = X-Khronos value from X-Gorgon generation
        data = Argus.get_sign(params=req.params,timestamp=req.timestamp,stub=req.stub)
        return Response({"x-argus":data}, headers={"Content-Type": "application/json"})
    except Exception as e:
        print(e)
        return None
    

@app.post("/xladon")
def xladon(req: XLadonDict):
    try:
        # timestamp = X-Khronos value from X-Gorgon generation
        data = Ladon.encrypt(timestamp=req.timestamp,license_id=req.license_id,aid=req.aid)
        return Response({"x-ladon":data}, headers={"Content-Type": "application/json"})
    except Exception as e:
        print(e)
        return None


# Start ASGI Server
# uvicorn main:app --reload --host 0.0.0.0 --port 8100

from fastapi import FastAPI, Request, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.websockets import WebSocketDisconnect
from starlette.websockets import WebSocketState
import asyncio
from chain import *
import numpy as np
from utils import *
import os
import json
import base64
import random
from callback import LLMCallbackHandler

split_page = os.environ.get('SPLIT_PAGE', 5)
app = FastAPI(websocket_ping_interval=10)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


async def wait_for_timeout(websocket: WebSocket, timeout: int = 20 * 60):
    await asyncio.sleep(timeout)
    if websocket.client_state != WebSocketState.DISCONNECTED:
        await websocket.close()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    timeout_task = asyncio.create_task(wait_for_timeout(websocket))

    try:
        while True:
            try:
                # 20분 동안 웹소켓 메시지를 기다린다.
                data = await asyncio.wait_for(websocket.receive_text(), timeout=20 * 60)
            except asyncio.TimeoutError:
                # 타임아웃이 발생하면 웹소켓 끝점을 종료한다.
                break

            data = json.loads(data)
            file_name, texts = handle_data(data)
            if texts is None:
                await websocket.send_text("Error")
            summarize_handler = LLMCallbackHandler(websocket)
            chain = get_chain(summarize_handler)
            printed_texts = []
            for doc in texts:
                # 데이터 생성
                # printed_text = 'asdfafsdf'
                printed_text = await chain.arun(doc)
                printed_texts.append(printed_text)
                # WebSocketManager를 사용하여 클라이언트에 데이터 전송
                await websocket.send_text(printed_text)

            for text in printed_texts:
                write_file(f"results/summarized_{file_name}.txt", text)
            await websocket.send_text("-----END-----")
            # await websocket.send_text(json.dumps(response_data))
    except WebSocketDisconnect:
        await websocket.close()
        timeout_task.cancel()


def handle_data(request: json):

    pdf_file = request["pdf_file"]
    text = request["text"]

    if not is_valid_url(text):
        if text:
            return None, None
    if pdf_file is None:
        pass
    else:
        pdf_file = pdf_file.split(",", 1)[1]
        pdf_file = base64.b64decode(pdf_file)
    docs = None
    randit_max = 100*100
    randit = random.randint(0, randit_max) + random.randint(0, randit_max) + random.randint(0, randit_max)
    file_name = f'doc{randit + random.randint(0, randit_max)}_{randit + random.randint(0, randit_max)}'

    # 파일과 텍스트 데이터 처리
    if pdf_file is not None:
        with open(f"uploaded_files/{file_name}.pdf", "wb") as buffer:
            buffer.write(pdf_file)
        buffer.close()
        docs = get_pdf_docs(f"uploaded_files/{file_name}.pdf", is_local=True)

    if text:
        docs = get_pdf_docs(text, is_local=False)

    if docs is None:
        return None, None

    split_pages = int(len(docs) / int(split_page))
    if split_pages == 0:
        split_pages = 1

    return file_name, np.array_split(docs, split_pages)

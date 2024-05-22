import websocket
import uuid
import json
import urllib.request
import urllib.parse
from PIL import Image
import io
import random

# 서버 주소와 클라이언트 ID 설정
server_address = "127.0.0.1:8188"
client_id = str(uuid.uuid4())

# 프롬프트를 큐에 넣는 함수
def queue_prompt(prompt):
    p = {"prompt": prompt, "client_id": client_id}
    data = json.dumps(p).encode('utf-8')
    req = urllib.request.Request(f"http://{server_address}/prompt", data=data)
    return json.loads(urllib.request.urlopen(req).read())

# 이미지를 가져오는 함수
def get_image(filename, subfolder, folder_type):
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    url_values = urllib.parse.urlencode(data)
    with urllib.request.urlopen(f"http://{server_address}/view?{url_values}") as response:
        return response.read()

# 히스토리를 가져오는 함수
def get_history(prompt_id):
    with urllib.request.urlopen(f"http://{server_address}/history/{prompt_id}") as response:
        return json.loads(response.read())

# WebSocket을 통해 이미지를 가져오는 함수
def get_images(ws, prompt):
    prompt_id = queue_prompt(prompt)['prompt_id']
    output_images = {}
    while True:
        out = ws.recv()
        if isinstance(out, str):
            message = json.loads(out)
            if message['type'] == 'executing':
                data = message['data']
                if data['node'] is None and data['prompt_id'] == prompt_id:
                    break  # 실행 완료
        else:
            continue  # 미리보기는 바이너리 데이터

    history = get_history(prompt_id)[prompt_id]
    for node_id in history['outputs']:
        node_output = history['outputs'][node_id]
        if 'images' in node_output:
            images_output = []
            for image in node_output['images']:
                image_data = get_image(image['filename'], image['subfolder'], image['type'])
                images_output.append(image_data)
            output_images[node_id] = images_output

    return output_images

# JSON 워크플로우 파일 읽기
with open("1654.json", "r", encoding="utf-8") as f:
    workflow_data = f.read()

workflow = json.loads(workflow_data)

# 계속 같은사진만 나와 시드 값 랜덤화
workflow["12"]["inputs"]["seed"] = random.randint(0, 2**32 - 1)

# # 프롬프트 수정 (예제 프롬프트로 대체 가능)
# workflow["17"]["inputs"]["text"] = ""
# workflow["18"]["inputs"]["text"] = ""

# WebSocket 연결
ws = websocket.WebSocket()
ws.connect(f"ws://{server_address}/ws?clientId={client_id}")

# 이미지 가져오기
images = get_images(ws, workflow)

# 출력된 이미지 표시
for node_id in images:
    for image_data in images[node_id]:
        image = Image.open(io.BytesIO(image_data))
        image.show()

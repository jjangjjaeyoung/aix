import json
from ComfyUI import ComfyUI, load_checkpoint, load_lora, encode_text, generate_image, save_image

# JSON 파일 로드
with open('comfy_api.json', 'r') as f:
    workflow = json.load(f)

# ComfyUI 초기화
ui = ComfyUI()

# 체크포인트 및 LoRA 파일 로드
ui.load_checkpoint(workflow['4']['inputs']['ckpt_name'])
ui.load_lora(workflow['22']['inputs']['lora_name'], strength_model=1, strength_clip=1)
ui.load_lora(workflow['10']['inputs']['lora_name'], strength_model=1, strength_clip=1)

# 텍스트 인코딩
prompt_encoding = ui.encode_text(workflow['6']['inputs']['text'])
negative_prompt_encoding = ui.encode_text(workflow['7']['inputs']['text'])

# 이미지 생성
latent_image = ui.generate_latent_image(width=workflow['5']['inputs']['width'], height=workflow['5']['inputs']['height'], batch_size=workflow['5']['inputs']['batch_size'])
generated_images = ui.generate_image(prompt_encoding, negative_prompt_encoding, latent_image, steps=workflow['3']['inputs']['steps'], cfg=workflow['3']['inputs']['cfg'], sampler_name=workflow['3']['inputs']['sampler_name'])

# 이미지 저장
ui.save_image(generated_images, filename_prefix=workflow['9']['inputs']['filename_prefix'])

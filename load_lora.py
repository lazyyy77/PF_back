import requests


url = "http://127.0.0.1:8011"
lora_path = "qingpingwan/Qwen2.5-7B-Lora-Law"
# lora_path = "yis77/lora32b"
agent_num = 100

for i in range(agent_num + 1):
    lora_name = f"lora{i}"
    response = requests.post(
        url + "/load_lora_adapter",
        json={
            "lora_name": lora_name,
            "lora_path": lora_path,
        },
    )
    if response.status_code == 200:
        print(f"LoRA adapter {lora_name} loaded successfully.")
    else:
        print(f"Failed to load LoRA adapter {lora_name}.", response.json())

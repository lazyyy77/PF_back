import openai

client = openai.Client(api_key="123", base_url="http://localhost:30000/v1")


response = client.chat.completions.create(
    model="Qwen/Qwen2.5-7B-Instruct",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "hello. how's the day?"}
    ],
    temperature=0.7,
    extra_body={"lora_path": "lora2"}
)

print(response)

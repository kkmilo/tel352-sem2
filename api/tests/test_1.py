import requests

with open("felipe1.jpg", "rb") as f:
    files = {"image": ("test.jpg", f, "image/jpeg")}
    r = requests.post("http://127.0.0.1:8000/predict/height", files=files)

print("Status:", r.status_code)
print("Height:", r.headers.get("X-Height-Predicted"))
print("Confidence:", r.headers.get("X-Confidence"))

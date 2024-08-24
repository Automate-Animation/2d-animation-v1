import requests

url = "http://localhost:49153/transcriptions?async=false"

payload = {}
files=[
  ('transcript',('story-2.txt',open('/home/oye/Documents/animation_software/2d-animation-v1/example/story/story-2.txt','rb'),'text/plain')),
  ('audio',('story-2-01.m4a',open('/home/oye/Documents/animation_software/2d-animation-v1/example/story/story-2-01.m4a','rb'),'application/octet-stream'))
]
headers = {}

response = requests.request("POST", url, headers=headers, data=payload, files=files)

print(response.text)

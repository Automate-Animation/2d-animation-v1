import requests


class TranscriptionService:
    def __init__(
        self,
        files,
        location=None,
        url="http://localhost:49153/transcriptions?async=false",
        headers=None,
        payload=None,
    ):
        self.url = url
        self.location = location
        self.files = files
        self.headers = headers or {}
        self.payload = payload or {}

    def send_request(self):
        # Open files in binary mode
        opened_files = [
            (name, (name, open(path, "rb"), content_type))
            for name, path, content_type in self.files
        ]

        # Make the POST request
        response = requests.post(
            self.url, headers=self.headers, data=self.payload, files=opened_files
        )

        # Close all opened files
        for _, (name, file, _) in opened_files:
            file.close()

        # Return the response as a JSON object
        try:
            return response.json()
        except ValueError:
            # Handle the case where response is not JSON
            print("Response content is not in JSON format.")
            return None


if __name__ == "__main__":
    url = "http://localhost:49153/transcriptions?async=false"
    files = [
        (
            "transcript",
            "/home/oye/Documents/animation_software/2d-animation-v1/example/story/story-2.txt",
            "text/plain",
        ),
        (
            "audio",
            "/home/oye/Documents/animation_software/2d-animation-v1/example/story/story-2-01.m4a",
            "application/octet-stream",
        ),
    ]

    service = TranscriptionService(files=files)
    response_json = service.send_request()
    print(response_json)

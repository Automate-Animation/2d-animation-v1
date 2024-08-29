import requests
import json


class TranscriptionService:
    def __init__(
        self,
        files,
        location=None,
        url="http://localhost:49153/transcriptions?async=false",
        headers=None,
        payload=None,
    ):
        print("Initializing TranscriptionService...")
        self.url = url
        self.location = location
        self.files = files
        self.headers = headers or {}
        self.payload = payload or {}

    def send_request(self):
        print("Preparing to send request...")

        # Open files in binary mode
        opened_files = []
        for name, path, content_type in self.files:
            try:
                print(f"Opening file: {path}")
                opened_files.append((name, (name, open(path, "rb"), content_type)))
            except Exception as e:
                print(f"Error opening file {path}: {e}")
                return None

        print("Files opened successfully. Sending POST request...")
        # Make the POST request
        try:
            response = requests.post(
                self.url, headers=self.headers, data=self.payload, files=opened_files
            )
            print("Request sent. Awaiting response...")
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            for _, (name, file, _) in opened_files:
                file.close()
            return None

        # Close all opened files
        for _, (name, file, _) in opened_files:
            file.close()
        print("Files closed.")

        # Return the response as a JSON object
        try:
            print("Attempting to parse response as JSON...")
            return response.json()
        except ValueError:
            print("Response content is not in JSON format.")
            return None


if __name__ == "__main__":
    print("Starting main execution...")
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
    print(f"Response JSON: {response_json}")

    if response_json is not None:
        print("Saving response to output_fi.json...")
        with open("output_fi.json", "w") as json_file:
            json.dump(response_json, json_file, indent=4)
        print("Response saved.")
    else:
        print("No response to save.")

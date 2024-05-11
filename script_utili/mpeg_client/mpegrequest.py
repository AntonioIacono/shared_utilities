import requests

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python3 mpegrequest.py file.mpeg http://10.10.11.2:8080/")
    else:
# Example usage:
        url = sys.argv[2] #Replace with the actual URL of the server
        video_path = sys.argv[1]  # Replace with the path to the example.docx fi>

	# Set the headers with the Content-Type
        headers = {"Content-Type": "video/mpeg"}

	# Open the video file and send a POST request
        with open(video_path, 'rb') as video_file:
    	     response = requests.post(url, headers=headers, data=video_file.read())

	# Print the response
        print(response.status_code)
        print(response.text)

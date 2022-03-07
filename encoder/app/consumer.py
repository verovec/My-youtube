import pika, os, json, requests
from videoprops import get_video_properties
import requests

resolutions = {
	"2160": {
		"dimensions": "3840x2160",
		"next": "1440"
	},
	"1440": {
		"dimensions": "2560x1440",
		"next": "1080"
	},
	"1080": {
		"dimensions": "1920x1080",
		"next": "720"
	},
	"720": {
		"dimensions": "1280x720",
		"next": "480"
	},
	"480": {
		"dimensions": "854x480",
		"next": "360"
	},
	"360": {
		"dimensions": "640x360",
		"next": "240"
	},
	"240": {
		"dimensions": "426x240",
		"next": None
	}
}

HOST = "http://api:5000"
UPLOAD_FOLDER = "/uploads/"

def getNearestResolution(resolution):
    if resolution in resolutions:
        return resolution
    for res in resolutions:
        if int(resolution) > int(res):
            return res

def getVideoResolution(filename):
	props = get_video_properties(UPLOAD_FOLDER + filename)
	return getNearestResolution(str(props['height']))

def encodeVideoInLowerResolutions(body, resolution):
	resolutionObject = resolutions[resolution]
	if resolutionObject["next"] == None:
		return
	nextResolution = resolutions[resolutionObject["next"]]
	fileBasepath = UPLOAD_FOLDER + body["filenameWithoutExtension"]
	output = fileBasepath + "_" + resolutionObject["next"] + "p.mp4"
	os.system("ffmpeg -i '" + fileBasepath + body["extension"] + "' -c:a copy -s '" + nextResolution["dimensions"] + "' '" + output + "'")
	requests.patch(HOST + "/video/" + str(body["video_ids"]) + "?file=" + output + "&format=" + resolutionObject["next"])
	if (nextResolution["next"] != None):
		encodeVideoInLowerResolutions(body, resolutionObject["next"])

def encodeVideos(ch, method, properties, body):
	body = json.loads(body)
	resolution = getVideoResolution(body["filename"])
	encodeVideoInLowerResolutions(body, resolution)
	requests.post("http://mailer:5001/mail/send_mail?type=encoding&mail_address=" + body['email'])

credentials = pika.PlainCredentials(os.environ.get('RABBITMQ_DEFAULT_USER', 'guest'), os.environ.get('RABBITMQ_DEFAULT_PASS', 'guest'))
params = pika.ConnectionParameters('rabbitmq', 5672, credentials=credentials)

connection = pika.BlockingConnection(params)
channel = connection.channel()
channel.queue_declare(queue='videoCreation')
channel.basic_consume(queue='videoCreation', on_message_callback=encodeVideos, auto_ack=True)
channel.start_consuming()
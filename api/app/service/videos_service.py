import random, datetime, os, json, pika
from os.path import join, dirname, realpath
from werkzeug.utils import secure_filename
from mutagen.mp4 import MP4
from elasticsearch import Elasticsearch, RequestsHttpConnection
from datetime import datetime
import traceback
import json

import sys
sys.path.append("..")

from app import database

from utils.hash import sha256, hash_id
from utils.Logger import Logger
from utils.ApiResponse import ApiResponse
from utils.utils import handleLimits

from model.Video import Video
from model.User import User
from model.Comment import Comment
from model.JWToken import JWToken

logger = Logger()

class VideosService():
    authorized_updates = [
        "name",
        "description"
    ]

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

    UPLOAD_FOLDER = "/uploads/"
    ALLOWED_EXTENSIONS = {'mov', 'avi', 'mp4'}

    @staticmethod
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in VideosService.ALLOWED_EXTENSIONS

    @staticmethod
    def createVideo(video_data: dict):
        """
        Creates a video in the database.
        """
        response = ApiResponse()
        sql_datetime = datetime.utcnow()
        if VideosService.allowed_file(video_data['file'].filename):
            extension = os.path.splitext(video_data['file'].filename)[1]
            video_ids = sha256(hash_id(random.randint(1, 9999)) + video_data["filename"])
            filenameWithoutExtension = video_ids
            filename = filenameWithoutExtension + extension
            filepath = os.path.join(VideosService.UPLOAD_FOLDER, secure_filename(filename))
            video_data['file'].save(filepath)
            video = Video(
                ids=video_ids,
                name=video_data['name'],
                description=video_data['description'],
                filename=video_data['filename'],
                user_ids=video_data['user_ids'],
                path=filepath,
                duration=VideosService.get_video_duration(filename),
                created_at=sql_datetime,
                updated_at=sql_datetime
            )
            try:
                es = Elasticsearch(
                    "https://elastic:elasticpwd@es01:9200",
                    verify_certs=False,
                    connection_class=RequestsHttpConnection
                )
                es.indices.create(index='video', ignore=400)
                es.index(index="video", body={
                    "ids": video.ids,
                    "name": video.name,
                    "description": video.description,
                    "created_at": video.created_at,
                    "user_id": video.user_ids,
                    "pseudo": video_data['user_pseudo'],
                    "duration": video.duration
                })
                body = {
                    "filenameWithoutExtension": filenameWithoutExtension,
                    "filename": filename,
                    "extension": extension,
                    "video_ids": video.ids,
                    "email": video_data['user_email']
                }
                credentials = pika.PlainCredentials(os.environ.get('RABBITMQ_DEFAULT_USER', 'guest'), os.environ.get('RABBITMQ_DEFAULT_PASS', 'guest'))
                params = pika.ConnectionParameters('rabbitmq', 5672, credentials=credentials)
                connection = pika.BlockingConnection(params)
                channel = connection.channel()
                channel.basic_publish(exchange='', routing_key='videoCreation', body=json.dumps(body))
                response.setSuccess()
                response.setMessage("Successfuly created video")
                response.setDetails({
                    "id": video_ids,
                    "name": video.name
                })
                if database.save_changes(video) is False:
                    response.setMessage("An error occured while persisting data to the database")
            except Exception as e:
                print(e)
                response.setMessage("An error occured while uploading your video")
                
        else:
            response.setMessage("Can't upload this file")
        return response

    @staticmethod
    def getVideoFromName(name: str, interval: int, page: int):
        """
        Get a video in the database from its name.
        """
        response = ApiResponse()
        limits_response = handleLimits(Video, page, interval)
        if limits_response.error == False:
            page = limits_response.details["page"]
            interval = limits_response.details["interval"]
            offset = page * interval - interval
            videos = VideosService.getVideosByData(offset, interval, {"name": name})
            if len(videos):
                response.setSuccess()
                response.setMessage("{} Video found".format(len(videos)))
                response.setDetails({
                    "data": videos,
                    "pager": {
                        "current": page,
                        "total": limits_response.details["total_nb_pages"]
                    }
                })
            else:
                response.setMessage("Impossible to find a video")
        return response

    @staticmethod
    def searchDBVideosByData(offset: int, interval: int, data):
        """Search videos in database by data criterias"""
        videos = []
        try:
            query = Video.query
            if "ids" in data and data["ids"] and len(data["ids"]):
                query = query.filter(Video.ids==data['ids'])
            if "name" in data and data["name"] and len(data["name"]):
                query = query.filter(Video.name.like("%" + data['name'] + "%"))
            if "pseudo" in data and data["pseudo"] and len(data["pseudo"]):
                user = User.query.filter_by(pseudo=data['pseudo']).first()
                query = query.filter_by(user_ids=user.ids)
            if "duration" in data and data["duration"] and len(data["duration"]):
                query = query.filter(Video.duration==data['duration'])
            videos = query.order_by(Video.name.desc()).limit(interval).offset(offset).all()
        except Exception as e:
            print(traceback.format_exc())
            print(e)
            videos = []
        return videos

    @staticmethod
    def getDBVideosByData(offset: int, interval: int, data):
        videos = []
        db_videos = VideosService.searchDBVideosByData(offset, interval, data)
        if len(db_videos):
            for video in db_videos:
                user = User.query.filter_by(ids=video.user_ids).first()
                videos.append({
                    "id": video.ids,
                    "name": video.name,
                    "filename": video.filename,
                    "format": video.format,
                    "duration": video.duration,
                    "description": video.description if video.description and len(video.description) else "",
                    "user_id": video.user_ids,
                    "user_pseudo": user.pseudo,
                    "created_at": str(video.created_at)
                })
        return videos

    @staticmethod
    def searchESVideosByData(offset: int, interval: int, data):
        """Search videos in Elasticsearch by data criterias"""
        videos = []
        try:
            es = Elasticsearch(
                "https://elastic:elasticpwd@es01:9200",
                verify_certs=False,
                connection_class=RequestsHttpConnection
            )
            base_query = {
                "query": {
                    "bool": {
                        "must": [
                            {
                                "wildcard": { "name": "*" }
                            }
                        ]
                    }
                }
            }
            if "name" in data and data["name"] and len(data["name"]):
                base_query["query"]["bool"]["must"][0] = {"wildcard": { "name": "*" + data['name'] + "*" }}
            if "pseudo" in data and data["pseudo"] and len(data["pseudo"]):
                base_query["query"]["bool"]["must"].append( {"wildcard": { "pseudo": "*" + data["pseudo"] + "*"}} )
            if "duration" in data and data["duration"] and len(data["duration"]):
                base_query["query"]["bool"]["must"].append( {"wildcard": { "duration": data['duration'] }} )
            videos_search = es.search(index="video", body=base_query, from_=offset, size=interval)
            if len(videos_search["hits"]["hits"]):
                videos = videos_search["hits"]["hits"]
        except Exception as e:
            print(traceback.format_exc())
            print(e)
            videos = []
        return videos

    @staticmethod
    def getESVideosByData(offset: int, interval: int, data):
        videos = []
        es_videos = VideosService.searchESVideosByData(offset, interval, data)
        if len(es_videos):
            for video in es_videos:
                video_data = video["_source"]
                videos.append({
                    "id": video_data["ids"],
                    "name": video_data["name"],
                    "description": video_data["description"],
                    "duration": video_data["duration"],
                    "user_id": video_data["user_id"],
                    "pseudo": video_data["pseudo"],
                    "created_at": video_data["created_at"]
                })
        return videos
    
    @staticmethod
    def getVideosByData(offset: int, interval: int, data):
        indices = {}
        videos = []
        es_videos = VideosService.getESVideosByData(offset, interval, data)
        db_videos = VideosService.getDBVideosByData(offset, interval, data)
        for video in es_videos:
            if video["id"] not in indices:
                videos.append(video)
                indices[video["id"]] = True
        for video in db_videos:
            if video["id"] not in indices:
                videos.append(video)
                indices[video["id"]] = True
        return videos
    
    @staticmethod
    def getVideoByIds(ids: str):
        response = ApiResponse()
        videos = VideosService.getDBVideosByData(0, 1, { "ids": ids })
        if len(videos):
            video = videos[0]
            response.setMessage("Video found")
            response.setDetails(video)
            response.setSuccess()
        else:
            response.setMessage("Impossible to find any video with this ID")
        return response

    @staticmethod
    def listVideos(page: int, interval: int, data):
        """
        List all video in the database using optional data criterias.
        """
        response = ApiResponse()
        limits_response = handleLimits(Video, page, interval)
        if limits_response.error == False:
            page = limits_response.details["page"]
            interval = limits_response.details["interval"]
            offset = page * interval - interval
            videos = VideosService.getVideosByData(offset, interval, data)
            if len(videos):
                response.setSuccess()
                response.setMessage("{} Video found".format(len(videos)))
                response.setDetails({
                    "data": videos,
                    "pager": {
                        "current": page,
                        "total": limits_response.details["total_nb_pages"]
                    }
                })
            else:
                response.setMessage("Impossible to find any video")
        return response

    @staticmethod
    def getVideoByName(video_name: str, interval: int, page: int):
        """
        Get a video in the database by the name field.
        """
        response = VideosService.getVideoFromName(video_name, interval, page)
        return response

    @staticmethod
    def updateVideo(video: Video, updates: dict):
        """
        Update a video in the database.
        """
        response = ApiResponse()
        if video is not None:
            perform_update = False
            for parameter in updates:
                if parameter in VideosService.authorized_updates:
                    if getattr(video, parameter) != updates[parameter] and updates[parameter] != None:
                        perform_update = True
                        setattr(video, parameter, updates[parameter])
            if perform_update:
                video.updated_at = datetime.utcnow()
                if database.save_changes(video) is False:
                    response.setMessage("An error occured while saving video's details")
                else:
                    logger.info("[VideosService.updateVideo] {} updated its video".format(video.name))
                    response.setMessage("Video successfuly updated")
                    response.setSuccess()
            if len(response.message) == 0:
                response.setMessage("Nothing was updated")
                response.setSuccess()
        else:
            response.setMessage("Impossible to find your Video")
        return response

    @staticmethod
    def updateVideoByIds(user_requesting: User, video_ids: str, updates: dict):
        """
        Update a video in the database by ids field.
        """
        response = ApiResponse()
        video = Video.query.filter_by(ids=video_ids).first()
        if video is not None:
            if video.user_ids == user_requesting.ids:
                return VideosService.updateVideo(video, updates)
            else:
                response.setMessage("You are not authorized to update this video")
        else:
            response.setMessage("Impossible to find this video")
        return response

    @staticmethod
    def deleteVideo(video: Video):
        """
        Delete a video in the database.
        """
        response = ApiResponse()
        if video is not None:
            if database.delete(video) is False:
                response.setMessage("An error occured while deleting this video")
            else:
                os.remove(os.path.join(VideosService.UPLOAD_FOLDER, video.filename))
                logger.info("[VideosService.deleteVideo] {} was deleted".format(video.name))
                response.setMessage("Video successfuly deleted")
                response.setSuccess()
        else:
            response.setMessage("Impossible to find this video")
        return response

    @staticmethod
    def deleteVideoByID(user_requesting: User, video_ids: str):
        """
        Delete a video in the database by ids field.
        """
        response = ApiResponse()
        video = Video.query.filter_by(ids=video_ids).first()
        if video is not None:
            if video.user_ids == user_requesting.ids:
                return VideosService.deleteVideo(video)
            else:
                response.setMessage("You are not authorized to delete this video")
        else:
            response.setMessage("Impossible to find this video")
        return response

    @staticmethod
    def getCommentByVideoID(video_ids: str, interval: int, page: int):
        response = ApiResponse()
        limits_response = handleLimits(Comment, page, interval)
        if limits_response.error == False:
            page = limits_response.details["page"]
            interval = limits_response.details["interval"]
            offset = page * interval - interval
            comments = Comment.query.filter_by(video_ids=video_ids).order_by(Comment.created_at.desc()).limit(interval).offset(offset).all()
            if len(comments) != 0:
                response.setSuccess()
                response.setMessage("{} Comment found".format(len(comments)))
                data = list()
                for comment in comments:
                    user = User.query.filter_by(ids=comment.user_ids).first()
                    data.append({
                        "user_pseudo": user.pseudo,
                        "user_ids": comment.user_ids,
                        "video_ids": comment.video_ids,
                        "content": comment.content,
                        "updated_at": str(comment.updated_at),
                        "created_at": str(comment.created_at)
                    })
                response.setDetails({
                    "data": data,
                    "pager": {
                        "current": page,
                        "total": limits_response.details["total_nb_pages"]
                    }
                })
            else:
                response.setMessage("Impossible to find any comment")
        return response

    @staticmethod
    def addCommentByVideoID(user_requesting: User, comment_data: dict):
        response = ApiResponse()
        sql_datetime = datetime.utcnow()
        comment = Comment(
            ids=sha256(hash_id(random.randint(1, 9999)) + comment_data["content"]),
            content=comment_data['content'],
            user_ids=comment_data['user_ids'],
            video_ids=comment_data["video_ids"],
            created_at=sql_datetime,
            updated_at=sql_datetime
        )
        if database.save_changes(comment) is False:
            response.setMessage("An error occured while persisting data to the database")
        else:
            response.setSuccess()
            response.setMessage("Successfuly created comment")
        return response

    @staticmethod
    def get_video_duration(filename):
        audio = MP4(VideosService.UPLOAD_FOLDER + filename)
        return str(round(int(audio.info.length)))

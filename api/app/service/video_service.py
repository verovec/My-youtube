import random, os, datetime, json
from os.path import join, dirname, realpath
from pathlib import Path

import sys
sys.path.append("..")

from app import database

from utils.Logger import Logger
from utils.ApiResponse import ApiResponse
from service.videos_service import VideosService

from model.Video import Video

logger = Logger()

class VideoService():

    @staticmethod
    def getVideoPath(ids: str, format: str):
        response = ApiResponse()
        videos = VideosService.getDBVideosByData(0, 1, { "ids": ids })
        if len(videos) == 0:
            response.setMessage("Can't find a video with this ID")
            return response
        video = videos[0]
        if format not in video["format"]:
            response.setMessage("Invalid format for that video")
            return response
        video_path = Path(video["format"][format])
        response.setDetails({
            "path": video_path,
            "filename": video_path.name,
            "parent": video_path.parent
        })
        response.setSuccess()
        return response
    
    @staticmethod
    def add_format(file: str, format: str, ids: str):
        response = ApiResponse()
        video = Video.query.filter_by(ids=ids).first()
        formats = {} if video.format is None else video.format
        formats[format] = file
        Video.query.filter_by(ids=video.ids).update(dict(format=formats))
        if database.save_changes() is False:
            response.setMessage("An error occured while saving video's details")
        else:
            logger.info("[VideosService.updateVideo] {} updated its video".format(video.name))
            response.setMessage("Video successfuly updated")
            response.setSuccess()
        return response

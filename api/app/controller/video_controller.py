from flask import request, escape, send_from_directory
from flask_restplus import Resource, Namespace, fields

import sys
sys.path.append("..")

from service.video_service import VideoService
from service.videos_service import VideosService
from service.user_service import UserService
from service.auth_service import AuthService, requires_authentication

from utils.ApiResponse import ApiResponse

import werkzeug

api = Namespace('Video', description='Listing video operations')

video_response_dto = api.model('video_response', {
    'error': fields.Boolean(description="True on error, false on success"),
    'message': fields.String(description="Some error or success message")
})

video_model_dto = api.parser()
video_model_dto.add_argument('file', help="Path to the formatted video", required=True)
video_model_dto.add_argument('format', help="Format of video", required=True)

video_file_model_dto = api.parser()
video_file_model_dto.add_argument('format', help="Format of video", required=True)

@api.route('/<id>')
@api.doc(params={'id': 'Video identifier (ids)'})
class Video(Resource):
    
    @api.expect(video_model_dto, validate=True)
    def patch(self, id):
        format = request.args.get('format')
        file = request.args.get('file')
        return VideoService.add_format(file, format, id).getResponse()
    
    def get(self, id):
        return VideosService.getVideoByIds(id).getResponse()

@api.route('/file/<id>')
@api.doc(params={'id': 'Video identifier (ids)'})
class Video(Resource):
    
    @api.expect(video_file_model_dto, validate=True)
    def get(self, id):
        format = escape(request.args.get('format'))
        video_path_response = VideoService.getVideoPath(id, format)
        if video_path_response.error:
            return video_path_response.getResponse()
        video_details = video_path_response.getResponse()
        return send_from_directory(video_details["data"]["parent"], video_details["data"]["filename"])

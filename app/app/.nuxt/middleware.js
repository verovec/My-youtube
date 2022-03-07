const middleware = {}

middleware['authentication'] = require('../middleware/authentication.js')
middleware['authentication'] = middleware['authentication'].default || middleware['authentication']

middleware['user'] = require('../middleware/user.js')
middleware['user'] = middleware['user'].default || middleware['user']

middleware['video'] = require('../middleware/video.js')
middleware['video'] = middleware['video'].default || middleware['video']

export default middleware

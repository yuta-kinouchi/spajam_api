from controllers import *
 
app.add_api_route('/', index)
app.add_api_route('/ai-talk', ai_talk)

from resources.users import (UserLogin, 
                            UserRegister, 
                            User, 
                            UserList, 
                            TokenRefresh,
                            UserLogout,
                            ChangePassword,)
from resources.images import (Image,
                                ImageUpload,
                                Avatar,
                                AvatarUpload)

def __init_users_routes__(api):
    api.add_resource(UserRegister, '/register')
    api.add_resource(User, '/user/<int:user_id>')
    api.add_resource(UserLogin, '/login')
    api.add_resource(TokenRefresh, '/refresh')
    api.add_resource(UserLogout, '/logout')
    api.add_resource(UserList, '/users')
    api.add_resource(ChangePassword, '/changepwd/<int:_id>')
    api.add_resource(ImageUpload, "/upload/image") # Upload Image
    api.add_resource(Image, "/img/<string:filename>") # Fetch Uploaded Image by Name
    api.add_resource(AvatarUpload, "/upload/avatar") # Upload User Profile Avatar
    api.add_resource(Avatar, "/avatar/<int:_id_>") # Fetch User Profile Avatar by User ID
from ai_os.security.identity import Role

class RequestContext:
    def __init__(self, user_id : str , role: Role):
        
        self.user_id = user_id
        self.role = role

class User:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.username = None
        self.password = None

    def from_dict(self, data: dict):
        self.username = data.get("username")
        self.password = data.get("password")
        return self

    def to_dict(self):
        return {
            "_id": self.user_id,
            "username": self.username,
            "password": self.password
        }

login_json_schema = {
    'type': 'object',
    'properties': {
        'username': {'type': 'string', "minLength": 3},
        'password': {'type': 'string', "minLength": 6},
    },
    'required': ['username', 'password']
}

register_json_schema = {
    'type': 'object',
    'properties': {
        'username': {'type': 'string', "minLength": 3},
        'password': {'type': 'string', "minLength": 6},
    },
    'required': ['username', 'password']
}
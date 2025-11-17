class Config:
    def __init__(self, host='127.0.0.1', port=8080):
        self.host = host
        self.port = port

    @classmethod
    def from_dict(cls, config_dict):
        host = config_dict.get('host', '127.0.0.1')
        port = config_dict.get('port', 8080)
        return cls(host, port)

    def to_dict(self):
        return {
            'host': self.host,
            'port': self.port
        }

    def __str__(self):
        return f'Config(host={self.host}, port={self.port})'

class Config(object):
    DEBUG = True
    TESTING = False

class DevelopmentConfig(Config):
    SECRET_KEY = "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"

config = {
    'development': DevelopmentConfig,
    'testing': DevelopmentConfig,
    'production': DevelopmentConfig
}

## Enter your Open API Key here
OPENAI_API_KEY = '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'

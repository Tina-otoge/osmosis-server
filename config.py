import os


def _get(env_name, fallback=None):
    return os.environ.get(env_name, fallback)


class Config:
    APP_NAME = _get('APP_NAME', 'osmosis')
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = _get(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = _get('SECRET_KEY', 'set a fucking key')
    LOGS_PATH = _get('LOGS_DIR', 'logs')
    LINKS = {
        'FORK': 'https://github.com/skielred/osumosis',
        'DOTNET': 'https://dotnet.microsoft.com/download/dotnet-core/3.1',
        'PUSHER': 'https://github.com/skielred/osmosis/releases/latest',
        'DISCORD': 'https://discord.gg/xWKFDBu',
        'REPO': 'https://github.com/skielred/osmosis',
        'DEV': 'https://tina.moe',
    }
    OSU_API_KEY = _get('OSU_API_KEY')
    BOARD_SIZE = 50
    MOMENT_DEFAULT_FORMAT = 'LLL'

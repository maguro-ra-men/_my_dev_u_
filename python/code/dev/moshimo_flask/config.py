class SystemConfig:
  DEBUG = True

  SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{user}:{password}@{host}/{db-name}?charset=utf8'.format(**{
      'user': 'kazu',
      'password': '11cRIudj9aSi',
      'host': 'localhost',
      'port':'50000',
      'db_name': 'dev_moshimo'
  })
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = False
Config = SystemConfig
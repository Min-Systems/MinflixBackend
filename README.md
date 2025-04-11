# MinflixBackend
# SQL Address Documentation
## Google Cloud
url_postgresql = f"postgresql+psycopg2://{db_user}:{db_password}@/{db_name}?host=/cloudsql/{instance_connection_name}"
## Local
url_postgresql = f"postgresql://{db_user}:{db_password}@localhost/{db_name}"
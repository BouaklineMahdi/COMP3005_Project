# app/config.py
import os

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "fitness_club")
DB_USER = os.getenv("DB_USER", "postgres")   # or your pgAdmin user
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

USE_ORM = os.getenv("USE_ORM", "false").lower() == "true"

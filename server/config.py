import os

class Settings:
    DOWNLOAD_DIR: str = "downloads"
    MAX_CONCURRENCY: int = 5
    MANUAL_URL_MAP: dict = {
        "Financial Modelling In Excel mangates": "https://mangates.com/financial-modeling-using-excel/",
    }
    USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

    def __init__(self):
        if not os.path.exists(self.DOWNLOAD_DIR):
            os.makedirs(self.DOWNLOAD_DIR)

settings = Settings()

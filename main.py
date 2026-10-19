from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yt_dlp

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class VideoData(BaseModel):
    url: str

@app.post("/download")
def get_video_link(data: VideoData):
    ydl_opts = {'format': 'best', 'quiet': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(data.url, download=False)
            return {
                "title": info.get("title"),
                "thumbnail": info.get("thumbnail"),
                "download_url": info.get("url")
            }
    except Exception as e:
        raise HTTPException(status_code=400, detail="गलत लिंक या वीडियो नहीं मिला")

@app.get("/")
def home():
    return {"status": "API चालू है!"}
  

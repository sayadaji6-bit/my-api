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

def get_best_direct_url(info):
    # 1. Agar direct single URL already hai
    if info.get("url"):
        return info.get("url")
    
    # 2. Formats me se audio+video wala best format dhoondo
    formats = info.get("formats", [])
    
    # Pehle audio aur video dono wala link dekhein
    for f in reversed(formats):
        if f.get("url") and f.get("vcodec") != "none" and f.get("acodec") != "none":
            return f.get("url")
            
    # Agar na mile to koi bhi working direct url
    for f in reversed(formats):
        if f.get("url"):
            return f.get("url")
            
    return None

@app.post("/download")
def get_video_link(data: VideoData):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        # Mobile app client use karne se blocks kam aate hain
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'ios', 'web']
            }
        },
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(data.url, download=False)
            
            # Agar playlist ho to pehla video lein
            if 'entries' in info:
                info = info['entries'][0]

            download_url = get_best_direct_url(info)
            
            if not download_url:
                raise HTTPException(status_code=400, detail="Is platform se direct download link nahi mil paya.")

            return {
                "title": info.get("title", "Video"),
                "thumbnail": info.get("thumbnail"),
                "download_url": download_url
            }
    except Exception as e:
        error_msg = str(e)
        if "Sign in to confirm" in error_msg or "bot" in error_msg:
            raise HTTPException(status_code=400, detail="Platform ne bot check lagaya hai. Kripya dusra link try karein.")
        raise HTTPException(status_code=400, detail=f"Error: {error_msg[:100]}")

@app.get("/")
def home():
    return {"status": "API chalu hai!"}
    

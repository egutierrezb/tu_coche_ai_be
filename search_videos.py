import scrapetube
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

#For calling this app we may invoke:  uvicorn search_videos:app --reload --host 0.0.0.0 --port 8000
@app.get("/videos")
async def search_channel_by_keyword(channel_id: str, keyword: str):
    videos = scrapetube.get_channel(channel_id=channel_id)
    results = []
    for v in videos:
        #print(f"JSON: {v}")
        title_data = v.get('title', {})
        # Safely get the text of the title
        title = ''
        if isinstance(title_data, dict) and 'runs' in title_data:
            title = title_data['runs'][0].get('text', '')

        if keyword.lower() in title.lower():
            vid = v.get('videoId')
            results.append(f"https://www.youtube.com/watch?v={vid}")
    return {
        "results": results
    }

#if __name__ == '__main__':
#    channel_id = "UC-kBlBK4icUzAN-2amwIRQA"  # Your channel ID
#    keyword = "Tsuru"
#    urls = search_channel_by_keyword(channel_id, keyword)
#    for url in urls:
#        print(url)


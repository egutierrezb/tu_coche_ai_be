from flask import Flask, request, jsonify
import scrapetube
import requests

def get_scrapetube_client():
    """Create a scrapetube client with browser-like headers."""
    session = requests.Session()
    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/115.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9"
    })
    scrapetube.requests = session
    return scrapetube

# Initialize Flask
app = Flask(__name__)

@app.route("/videos", methods=["GET"])
def search_channel_by_keyword():
    channel_id = request.args.get("channel_id")
    keyword = request.args.get("keyword")

    if not channel_id or not keyword:
        return jsonify({"error": "Missing channel_id or keyword"}), 400

    try:
        st = get_scrapetube_client()
        videos = st.get_channel(channel_id=channel_id)
        results = {}

        for v in videos:
            title_data = v.get('title', {})
            title = ''
            if isinstance(title_data, dict) and 'runs' in title_data:
                title = title_data['runs'][0].get('text', '')

            if keyword.lower() in title.lower():
                vid = v.get('videoId')
                results[title.lower()]=f"https://www.youtube.com/watch?v={vid}"

        return {"results": results}

    except Exception as e:
        return jsonify({
            "error": "Failed to fetch videos from YouTube",
            "details": str(e)
        }), 500

#For accessing locally:
#http://0.0.0.0:5001/videos?channel_id=UC-kBlBK4icUzAN-2amwIRQA&keyword=Tsuru
#For pythonanywhere:
#https://egutierrezb.pythonanywhere.com/apivideos/videos?channel_id=UC-kBlBK4icUzAN-2amwIRQA&keyword=Tsuru

#For flask we only need to "run" as is the python file
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
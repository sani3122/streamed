from flask import Flask, Response
import requests

app = Flask(__name__)

MAIN_URL = "https://streamed.pk"

@app.route("/")
def home():
    return "Streamed.pk M3U Playlist Generator is running successfully! Use your /playlist.m3u link in IPTV Player."

@app.route("/playlist.m3u")
def generate_m3u():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Referer": f"{MAIN_URL}/",
        "Origin": MAIN_URL
    }
    
    try:
        response = requests.get(f"{MAIN_URL}/api/matches/all", headers=headers, timeout=15)
        if response.status_code != 200:
            return "#EXTM3U\n#EXTINF:-1, Error fetching matches from streamed.pk", 200, {'Content-Type': 'audio/x-mpegurl'}
        
        matches = response.json()
    except Exception as e:
        error_msg = str(e).replace('\n', ' ')
        return f"#EXTM3U\n#EXTINF:-1, Connection Error: {error_msg}", 200, {'Content-Type': 'audio/x-mpegurl'}

    m3u_content = "#EXTM3U\n"
    
    for match in matches:
        title = match.get('title', 'Unknown Match')
        category = match.get('category', 'Other').upper()
        sources = match.get('sources', [])
        poster = match.get('poster', '')
        match_id = match.get('id', '')
        
        if poster and poster.startswith('/'):
            poster_url = MAIN_URL + poster
        else:
            poster_url = poster or "https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=500"
            
        if sources:
            # লাইভ ম্যাচগুলোর জন্য সোর্স যোগ করা
            for idx, src in enumerate(sources):
                source_name = src.get('source', 'server')
                stream_id = src.get('id', '')
                channel_name = f"[LIVE] [{category}] {title} (Server {idx+1})"
                
                # স্ট্রিম লিংক টার্গেট
                stream_link = f"{MAIN_URL}/watch/{match_id}"
                
                m3u_content += f'#EXTINF:-1 tvg-logo="{poster_url}" group-title="{category}",{channel_name}\n'
                m3u_content += f'{stream_link}\n'
        else:
            # আপকামিং ম্যাচগুলোর জন্য
            channel_name = f"[UPCOMING] [{category}] {title}"
            m3u_content += f'#EXTINF:-1 tvg-logo="{poster_url}" group-title="{category} - Upcoming",{channel_name}\n'
            m3u_content += f'{MAIN_URL}\n'

    return Response(m3u_content, mimetype="audio/x-mpegurl")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
  

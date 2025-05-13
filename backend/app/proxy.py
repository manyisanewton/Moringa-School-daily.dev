import requests
from flask import Blueprint, jsonify, request

proxy_bp = Blueprint("proxy", __name__, url_prefix="/proxy")

@proxy_bp.route("/youtube-videos", methods=["GET"])
def proxy_youtube_videos():
    RSS2JSON_API_KEY = "qaroytlfmvhtdcvktht1hraeubbedie4ggiogmaz"
    VIDEO_API = f"https://api.rss2json.com/v1/api.json?rss_url=https://www.youtube.com/feeds/videos.xml?channel_id=UC8butISFwT-Wl7EV0hUK0BQ&api_key={RSS2JSON_API_KEY}"
    try:
        response = requests.get(VIDEO_API)
        response.raise_for_status()
        data = response.json()
        items = data.get("items", [])
        formatted_items = [
            {
                "guid": item["guid"],
                "title": item["title"],
                "link": item["link"],
                "pubDate": item["pubDate"],
            }
            for item in items
        ]
        return jsonify({"items": formatted_items}), 200
    except requests.RequestException as e:
        return jsonify({"error": f"Failed to fetch YouTube videos: {str(e)}"}), 500

@proxy_bp.route("/devto-articles", methods=["GET"])
def proxy_devto_articles():
    ARTICLE_API = "https://dev.to/api/articles"
    try:
        response = requests.get(ARTICLE_API)
        response.raise_for_status()
        data = response.json()
        formatted_data = [
            {
                "id": article["id"],
                "title": article["title"],
                "url": article["url"],
                "published_at": article["published_at"],
            }
            for article in data
        ]
        return jsonify(formatted_data), 200
    except requests.RequestException as e:
        return jsonify({"error": f"Failed to fetch Dev.to articles: {str(e)}"}), 500

@proxy_bp.route("/devto-article/<int:article_id>", methods=["GET"])
def proxy_devto_article(article_id):
    ARTICLE_DETAIL_API = f"https://dev.to/api/articles/{article_id}"
    try:
        response = requests.get(ARTICLE_DETAIL_API)
        response.raise_for_status()
        return jsonify(response.json()), 200
    except requests.RequestException as e:
        return jsonify({"error": f"Failed to fetch Dev.to article: {str(e)}"}), 500

@proxy_bp.route("/devto-comments", methods=["GET"])
def proxy_devto_comments():
    article_id = request.args.get("a_id")
    if not article_id:
        return jsonify({"error": "Missing a_id parameter"}), 400
    COMMENTS_API = f"https://dev.to/api/comments?a_id={article_id}"
    try:
        response = requests.get(COMMENTS_API)
        response.raise_for_status()
        return jsonify(response.json()), 200
    except requests.RequestException as e:
        return jsonify({"error": f"Failed to fetch Dev.to comments: {str(e)}"}), 500

@proxy_bp.route("/podcasts", methods=["GET"])
def proxy_podcasts():
    RSS2JSON_API_KEY = "qaroytlfmvhtdcvktht1hraeubbedie4ggiogmaz"
    AUDIO_API = f"https://api.rss2json.com/v1/api.json?rss_url=https://feeds.simplecast.com/4r7G7Z8a&api_key={RSS2JSON_API_KEY}"
    try:
        response = requests.get(AUDIO_API)
        response.raise_for_status()
        data = response.json()
        items = data.get("items", [])
        formatted_items = [
            {
                "title": item["title"],
                "category": "Podcast",
                "date": item["pubDate"],
                "audio_url": item.get("enclosure", {}).get("url", ""),
            }
            for item in items
        ]
        return jsonify(formatted_items), 200
    except requests.RequestException as e:
        return jsonify({"error": f"Failed to fetch podcasts: {str(e)}"}), 500
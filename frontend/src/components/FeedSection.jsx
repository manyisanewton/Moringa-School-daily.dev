import React, { useState, useEffect } from "react";
import './FeedSection.css';
import axios from 'axios';

function Feed() {
  const [content, setContent] = useState([]);
  const [videos, setVideos] = useState([]);
  const [articles, setArticles] = useState([]);
  const [error, setError] = useState('');

  // Pagination states
  const [contentPage, setContentPage] = useState(1);
  const [videosPage, setVideosPage] = useState(1);
  const [articlesPage, setArticlesPage] = useState(1);
  const itemsPerPage = 3;

  // Modal states
  const [selectedVideo, setSelectedVideo] = useState(null);
  const [selectedArticle, setSelectedArticle] = useState(null);
  const [articleContent, setArticleContent] = useState(null);
  const [articleComments, setArticleComments] = useState([]);

  const RSS2JSON_API_KEY = 'qaroytlfmvhtdcvktht1hraeubbedie4ggiogmaz'; // Replace with your RSS2JSON API key if needed
  const VIDEO_API = `https://api.rss2json.com/v1/api.json?rss_url=https://www.youtube.com/feeds/videos.xml?channel_id=UCWv7vMbMWH4-V0ZXdmDpPBA&api_key=${RSS2JSON_API_KEY}`;
  const ARTICLE_API = 'https://dev.to/api/articles?tag=softwareengineering';

  // Helper function to check if a URL is a YouTube link
  const isYouTubeUrl = (url) => {
    return url && (url.includes('youtube.com') || url.includes('youtu.be'));
  };

  // Helper function to extract YouTube video ID
  const getYouTubeVideoId = (url) => {
    const regex = /(?:v=|\/)([0-9A-Za-z_-]{11})/;
    const match = url.match(regex);
    return match ? match[1] : null;
  };

  const paginate = (data, page) => {
    const start = (page - 1) * itemsPerPage;
    const end = start + itemsPerPage;
    return data.slice(start, end);
  };

  const closeModal = () => {
    setSelectedVideo(null);
    setSelectedArticle(null);
  };

  // Fetch data and store locally
  useEffect(() => {
    const fetchData = async () => {
      try {
        // Load from localStorage first, fetch if not present
        let storedVideos = JSON.parse(localStorage.getItem('videos') || '[]');
        let storedArticles = JSON.parse(localStorage.getItem('articles') || '[]');

        if (storedVideos.length === 0) {
          const videoResponse = await axios.get(VIDEO_API);
          storedVideos = videoResponse.data.items || [];
          localStorage.setItem('videos', JSON.stringify(storedVideos));
        }
        setVideos(storedVideos);

        if (storedArticles.length === 0) {
          const articleResponse = await axios.get(ARTICLE_API);
          storedArticles = articleResponse.data || [];
          localStorage.setItem('articles', JSON.stringify(storedArticles));
        }
        setArticles(storedArticles);

        // Combine content (videos and articles)
        const allContent = [
          ...storedVideos.map(video => ({
            id: video.guid,
            title: video.title,
            created_at: video.pubDate,
            category_name: 'Fullstack Development',
          })),
          ...storedArticles.map(article => ({
            id: article.id,
            title: article.title,
            created_at: article.published_at,
            category_name: 'DevOps',
          })),
        ];
        setContent(allContent);
      } catch (err) {
        console.error('Feed error:', err);
        setError('Failed to load feed');
      }
    };

    fetchData();
  }, []);

  // Fetch article details and comments when selected
  useEffect(() => {
    if (selectedArticle) {
      const fetchArticleDetails = async () => {
        try {
          // Simulate article content and comments from the initial article data
          const article = articles.find(a => a.id === selectedArticle.id);
          if (article) {
            setArticleContent({
              published_at: article.published_at,
              user: { name: article.user?.name || 'Unknown' },
              tag_list: article.tag_list || [],
              description: article.description || 'No description available',
              body_html: article.body_html || '<p>No full content available</p>',
            });
            // Simulate comments (Dev.to API doesn't provide comments directly via this endpoint)
            setArticleComments([
              { id_code: `comment-${article.id}-1`, user: { name: 'User1' }, body_html: '<p>Great article!</p>' },
              { id_code: `comment-${article.id}-2`, user: { name: 'User2' }, body_html: '<p>Very informative.</p>' },
            ]);
          }
        } catch (err) {
          console.error('Error fetching article details:', err);
          setArticleContent(null);
          setArticleComments([]);
        }
      };
      fetchArticleDetails();
    } else {
      setArticleContent(null);
      setArticleComments([]);
    }
  }, [selectedArticle, articles]);

  return (
    <div>
      {error && <p style={{ color: 'red', textAlign: 'center' }}>{error}</p>}
      <div className="your-feed">
        <h2 className="title">CONTENT</h2>
        <div className="feed-grid">
          {content.length > 0 ? (
            paginate(content, contentPage).map((item) => (
              <div key={item.id} className="feed-cards">
                <span className="cat">{item.category_name}</span>
                <h3 className="feed-title">{item.title}</h3>
                <p className="date">{item.created_at}</p>
              </div>
            ))
          ) : (
            <p>No content available</p>
          )}
        </div>
        <div style={{ textAlign: 'center', marginTop: '1rem' }}>
          <button
            onClick={() => setContentPage((prev) => Math.max(prev - 1, 1))}
            disabled={contentPage === 1}
            style={{ marginRight: '10px', padding: '5px 10px' }}
          >
            Previous
          </button>
          <span>Page {contentPage}</span>
          <button
            onClick={() => setContentPage((prev) => prev + 1)}
            disabled={contentPage * itemsPerPage >= content.length}
            style={{ marginLeft: '10px', padding: '5px 10px' }}
          >
            Next
          </button>
        </div>
      </div>

      <div className="your-feed">
        <h2 className="title">YOUR VIDEOS</h2>
        <div className="feed-grid">
          {paginate(videos, videosPage).length > 0 ? (
            paginate(videos, videosPage).map((video) => (
              <div
                key={video.guid}
                className="feed-cards"
                onClick={() => setSelectedVideo(video)}
                style={{ cursor: 'pointer' }}
              >
                <span className="cat">Watch Video</span>
                <h3 className="feed-title">{video.title}</h3>
                <p className="date">{video.pubDate}</p>
              </div>
            ))
          ) : (
            <p>No videos available</p>
          )}
        </div>
        <div style={{ textAlign: 'center', marginTop: '1rem' }}>
          <button
            onClick={() => setVideosPage((prev) => Math.max(prev - 1, 1))}
            disabled={videosPage === 1}
            style={{ marginRight: '10px', padding: '5px 10px' }}
          >
            Previous
          </button>
          <span>Page {videosPage}</span>
          <button
            onClick={() => setVideosPage((prev) => prev + 1)}
            disabled={videosPage * itemsPerPage >= videos.length}
            style={{ marginLeft: '10px', padding: '5px 10px' }}
          >
            Next
          </button>
        </div>
      </div>

      <div className="your-feed">
        <h2 className="title">DEV ARTICLES</h2>
        <div className="feed-grid">
          {paginate(articles, articlesPage).length > 0 ? (
            paginate(articles, articlesPage).map((article) => (
              <div
                key={article.id}
                className="feed-cards"
                onClick={() => setSelectedArticle(article)}
                style={{ cursor: 'pointer' }}
              >
                <span className="cat">Read Article</span>
                <h3 className="feed-title">{article.title}</h3>
                <p className="date">{article.published_at}</p>
              </div>
            ))
          ) : (
            <p>No articles available</p>
          )}
        </div>
        <div style={{ textAlign: 'center', marginTop: '1rem' }}>
          <button
            onClick={() => setArticlesPage((prev) => Math.max(prev - 1, 1))}
            disabled={articlesPage === 1}
            style={{ marginRight: '10px', padding: '5px 10px' }}
          >
            Previous
          </button>
          <span>Page {articlesPage}</span>
          <button
            onClick={() => setArticlesPage((prev) => prev + 1)}
            disabled={articlesPage * itemsPerPage >= articles.length}
            style={{ marginLeft: '10px', padding: '5px 10px' }}
          >
            Next
          </button>
        </div>
      </div>

      {selectedVideo && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            zIndex: 1000,
          }}
        >
          <div
            style={{
              backgroundColor: '#fff',
              padding: '20px',
              borderRadius: '8px',
              width: '80%',
              maxWidth: '800px',
              position: 'relative',
            }}
          >
            <button
              onClick={closeModal}
              style={{
                position: 'absolute',
                top: '10px',
                right: '10px',
                background: 'none',
                border: 'none',
                fontSize: '1.5rem',
                cursor: 'pointer',
              }}
            >
              ×
            </button>
            <h3>{selectedVideo.title}</h3>
            <iframe
              width="100%"
              height="400"
              src={`https://www.youtube.com/embed/${getYouTubeVideoId(selectedVideo.link)}`}
              title={selectedVideo.title}
              frameBorder="0"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
            ></iframe>
          </div>
        </div>
      )}

      {selectedArticle && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            zIndex: 1000,
          }}
        >
          <div
            style={{
              backgroundColor: '#fff',
              padding: '20px',
              borderRadius: '8px',
              width: '80%',
              maxWidth: '800px',
              position: 'relative',
              maxHeight: '80vh',
              overflowY: 'auto',
            }}
          >
            <button
              onClick={closeModal}
              style={{
                position: 'absolute',
                top: '10px',
                right: '10px',
                background: 'none',
                border: 'none',
                fontSize: '1.5rem',
                cursor: 'pointer',
              }}
            >
              ×
            </button>
            <h3>{selectedArticle.title}</h3>
            {articleContent ? (
              <div>
                <p>Published on: {articleContent.published_at}</p>
                <p><strong>Author:</strong> {articleContent.user.name || 'Unknown'}</p>
                <p><strong>Tags:</strong> {Array.isArray(articleContent.tag_list) ? articleContent.tag_list.join(', ') : articleContent.tag_list || 'None'}</p>
                <p><strong>Description:</strong> {articleContent.description || 'No description available'}</p>
                <div
                  dangerouslySetInnerHTML={{
                    __html: articleContent.body_html.replace(
                      /src="\/([^"]+)"/g,
                      'src="https://dev.to/$1"'
                    ).replace(
                      /href="\/([^"]+)"/g,
                      'href="https://dev.to/$1"'
                    )
                  }}
                  style={{ lineHeight: '1.6', fontSize: '1rem', marginTop: '10px' }}
                />
                {articleComments.length > 0 && (
                  <div style={{ marginTop: '20px' }}>
                    <h4>Comments:</h4>
                    {articleComments.map(comment => (
                      <div key={comment.id_code} style={{ marginBottom: '10px', borderBottom: '1px solid #ccc', paddingBottom: '10px' }}>
                        <p><strong>{comment.user.name || 'Anonymous'}:</strong></p>
                        <div
                          dangerouslySetInnerHTML={{ __html: comment.body_html }}
                          style={{ lineHeight: '1.6', fontSize: '0.9rem' }}
                        />
                      </div>
                    ))}
                  </div>
                )}
                <p style={{ marginTop: '10px' }}>
                  <a
                    href={selectedArticle.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{ color: 'blue', textDecoration: 'underline' }}
                  >
                    Read the full article on Dev.to
                  </a>
                </p>
              </div>
            ) : (
              <p>Loading article details...</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default Feed;
import React, { useState, useEffect } from "react";
import Navbar from "../components/Navbar/UserNavbar";
import './Home2.css';
import FeedSection from "../components/FeedSection";
import CommentsCarousel from "../components/CommentsCarousel";
import Footer from "../components/Footer";
import axios from 'axios';

function Home2() {
  const [user, setUser] = useState({ name: 'User' });
  const [tags, setTags] = useState(['Full-Stack', 'Front-End', 'DevOps']);
  const [content, setContent] = useState([]);
  const [userContent, setUserContent] = useState([]);
  const [videos, setVideos] = useState([]);
  const [articles, setArticles] = useState([]);
  const [error, setError] = useState('');
  const [contentPage, setContentPage] = useState(1);
  const [videosPage, setVideosPage] = useState(1);
  const [articlesPage, setArticlesPage] = useState(1);
  const [filter, setFilter] = useState('All');
  const itemsPerPage = 6;

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

  // Our own fetching logic using the APIs
  const fetchVideos = async () => {
    try {
      const response = await axios.get(VIDEO_API);
      return response.data.items || [];
    } catch (err) {
      console.error('Failed to fetch videos:', err);
      setError('Failed to load videos');
      return [];
    }
  };

  const fetchArticles = async () => {
    try {
      const response = await axios.get(ARTICLE_API);
      return response.data || [];
    } catch (err) {
      console.error('Failed to fetch articles:', err);
      setError('Failed to load articles');
      return [];
    }
  };

  const fetchUserContentFromLocalStorage = () => {
    try {
      const storedPosts = JSON.parse(localStorage.getItem('pendingPosts') || '[]');
      return storedPosts;
    } catch (err) {
      console.error('Failed to fetch user content from localStorage:', err);
      setError('Failed to load user content');
      return [];
    }
  };

  useEffect(() => {
    const fetchFeedData = async () => {
      try {
        // Fetch videos
        const fetchedVideos = await fetchVideos();
        setVideos(fetchedVideos.slice(0, itemsPerPage * videosPage));

        // Fetch articles
        const fetchedArticles = await fetchArticles();
        setArticles(fetchedArticles.slice(0, itemsPerPage * articlesPage));

        // Combine content (videos and articles)
        const allContent = [
          ...fetchedVideos.map(video => ({
            id: video.guid,
            title: video.title,
            body: video.description || 'No description available',
            media_url: video.link,
            content_type: 'video',
            category_name: 'Fullstack Development',
            status: 'Published',
          })),
          ...fetchedArticles.map(article => ({
            id: article.id,
            title: article.title,
            body: article.description || 'No description available',
            media_url: article.url,
            content_type: 'article',
            category_name: 'DevOps',
            status: 'Published',
          })),
        ];
        setContent(allContent.slice(0, itemsPerPage * contentPage));

        // Fetch user content from localStorage
        const storedUserContent = fetchUserContentFromLocalStorage();
        setUserContent(storedUserContent);
      } catch (err) {
        console.error('Failed to fetch feed data:', err);
        setError('Failed to load feed');
      }
    };

    fetchFeedData();
  }, [contentPage, videosPage, articlesPage]);

  // Filter content based on selected filter
  const filteredContent = content.filter(item => {
    if (filter === 'All') return true;
    return item.content_type === filter.toLowerCase();
  });

  return (
    <div className="homepage">
      <Navbar />
      <main className="main-container">
        <section className="user-greeting">
          <h1>Hello, {user.name}</h1>
          <div className="tags">
            {tags.map((tag, index) => (
              <span key={index} className="tag">{tag}</span>
            ))}
          </div>
          <div className="filter-section">
            <label htmlFor="content-filter">Filter by: </label>
            <select
              id="content-filter"
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="filter-select"
            >
              <option value="All">All</option>
              <option value="Video">Video</option>
              <option value="Article">Article</option>
            </select>
        </div>
        </section>

        {/* Display User's Content */}
        {userContent.length > 0 && (
          <section className="user-content-section">
            <h2>Your Content</h2>
            <div className="content-list">
              {userContent.map((item) => (
                <div key={item.id} className="content-card">
                  <h3>{item.title}</h3>
                  <p>{item.body}</p>
                  <p><strong>Category:</strong> {item.category_name}</p>
                  <p><strong>Status:</strong> {item.status}</p>
                  {item.media_url && (
                    <div>
                      {item.media_url.startsWith('data:image/') ? (
                        <img src={item.media_url} alt={item.title} style={{ maxWidth: '300px' }} />
                      ) : item.media_url.startsWith('data:video/') ? (
                        <video width="320" height="240" controls>
                          <source src={item.media_url} type="video/mp4" />
                          Your browser does not support the video tag.
                        </video>
                      ) : null}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Pass filtered content to FeedSection */}
        <FeedSection
          content={filteredContent}
          videos={videos}
          articles={articles}
          audio={[]}
          error={error}
          contentPage={contentPage}
          setContentPage={setContentPage}
          videosPage={videosPage}
          setVideosPage={setVideosPage}
          articlesPage={articlesPage}
          setArticlesPage={setArticlesPage}
          audioPage={1}
          setAudioPage={() => {}} // No audio, so this is a no-op
          itemsPerPage={itemsPerPage}
        />
      </main>
      <CommentsCarousel />
      <Footer />
    </div>
  );
}

export default Home2;
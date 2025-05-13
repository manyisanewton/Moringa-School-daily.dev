import React, { useState, useEffect } from 'react';
import './Categories.css';
import Navbar from '../components/Navbar/UserNavbar';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faSearch, faChevronRight, faThumbsUp, faThumbsDown, faComment, faTimes, faBell, faBellSlash } from '@fortawesome/free-solid-svg-icons';
import Footer from '../components/Footer';
import axios from 'axios';

const Categories = () => {
  const [categories, setCategories] = useState([]);
  const [error, setError] = useState('');
  const [selectedPost, setSelectedPost] = useState(null);
  const [comments, setComments] = useState({});
  const [newComment, setNewComment] = useState({});
  const [searchTerm, setSearchTerm] = useState('');
  const [likes, setLikes] = useState({});
  const [dislikes, setDislikes] = useState({});
  const [hasLiked, setHasLiked] = useState({});
  const [subscriptions, setSubscriptions] = useState({});

  const RSS2JSON_API_KEY = 'qaroytlfmvhtdcvktht1hraeubbedie4ggiogmaz'; // Replace with your RSS2JSON API key if needed
  const VIDEO_API = `https://api.rss2json.com/v1/api.json?rss_url=https://www.youtube.com/feeds/videos.xml?channel_id=UCWv7vMbMWH4-V0ZXdmDpPBA&api_key=${RSS2JSON_API_KEY}`;
  const ARTICLE_API = 'https://dev.to/api/articles?tag=softwareengineering';

  const getCTA = (type) => {
    switch (type) {
      case 'video':
        return 'Watch Now';
      case 'article':
        return 'Read Article';
      default:
        return 'Explore';
    }
  };

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

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        // Fetch videos from YouTube via RSS2JSON
        const videoResponse = await axios.get(VIDEO_API);
        const videos = videoResponse.data.items || [];

        // Fetch articles from Dev.to
        const articleResponse = await axios.get(ARTICLE_API);
        const articles = articleResponse.data || [];

        // Load likes and comments from localStorage
        const storedLikes = JSON.parse(localStorage.getItem('likes') || '{}');
        const storedComments = JSON.parse(localStorage.getItem('comments') || '{}');

        // Map fetched data to categories
        const fetchedCategories = [
          {
            id: 1,
            name: 'Fullstack Development',
            description: 'Content related to fullstack development.',
            posts: [
              ...videos.slice(0, 3).map((item, index) => ({
                id: `video-${index + 1}`,
                type: 'video',
                title: item.title || 'No Title',
                author: item.author || 'Unknown',
                date: item.pubDate || new Date().toISOString(),
                url: item.link || '',
                likesCount: storedLikes[`video-${index + 1}`] || 0,
                dislikesCount: 0,
                comments: storedComments[`video-${index + 1}`] || [],
              })),
              ...articles.slice(0, 4).map((item, index) => ({
                id: `article-${index + 1}`,
                type: 'article',
                title: item.title || 'No Title',
                author: item.user?.name || 'Unknown',
                date: item.published_at || new Date().toISOString(),
                url: item.url || '',
                description: item.description || 'No description available.',
                likesCount: storedLikes[`article-${index + 1}`] || item.positive_reactions_count || 0,
                comments: storedComments[`article-${index + 1}`] || [],
              })),
            ],
          },
          {
            id: 2,
            name: 'Cyber Security',
            description: 'Content related to cybersecurity practices.',
            posts: [
              ...articles.slice(4, 8).map((item, index) => ({
                id: `article-${videos.length + index + 1}`,
                type: 'article',
                title: item.title || 'No Title',
                author: item.user?.name || 'Unknown',
                date: item.published_at || new Date().toISOString(),
                url: item.url || '',
                description: item.description || 'No description available.',
                likesCount: storedLikes[`article-${videos.length + index + 1}`] || item.positive_reactions_count || 0,
                comments: storedComments[`article-${videos.length + index + 1}`] || [],
              })),
            ],
          },
        ];

        setCategories(fetchedCategories);
        setLikes(storedLikes);
        setComments(storedComments);
        setError('');
      } catch (err) {
        setError('Failed to load categories or posts. Error: ' + (err.response?.data?.error || err.message));
        console.error('Fetch error:', err.response?.data || err.message);
        // Fallback data
        const fallbackData = [
          {
            id: 1,
            name: 'Fullstack Development',
            posts: [
              {
                id: 1,
                type: 'article',
                title: 'Sample Article',
                author: 'Sample Author',
                date: new Date().toISOString(),
                url: '',
                description: 'This is a sample article description.',
                likesCount: JSON.parse(localStorage.getItem('likes') || '{}')[1] || 10,
                comments: JSON.parse(localStorage.getItem('comments') || '{}')[1] || [],
              },
            ],
          },
          {
            id: 2,
            name: 'Cyber Security',
            posts: [
              {
                id: 1,
                type: 'article',
                title: 'Sample Article',
                author: 'Sample Author',
                date: new Date().toISOString(),
                url: '',
                description: 'This is a sample article description.',
                likesCount: JSON.parse(localStorage.getItem('likes') || '{}')[1] || 12,
                comments: JSON.parse(localStorage.getItem('comments') || '{}')[1] || [],
              },
            ],
          },
        ];
        setCategories(fallbackData);
      }
    };

    fetchCategories();
  }, []);

  const scrollRow = (direction, rowIndex) => {
    const row = document.querySelectorAll('.cards-row')[rowIndex];
    if (row) {
      const scrollAmount = direction === 'left' ? -300 : 300;
      row.scrollBy({ left: scrollAmount, behavior: 'smooth' });
    }
  };

  const handleLike = (postId) => {
    if (hasLiked[postId]) return; // Prevent multiple likes
    setLikes((prev) => ({
      ...prev,
      [postId]: (prev[postId] || 0) + 1,
    }));
    setHasLiked((prev) => ({ ...prev, [postId]: true }));
    setCategories((prevCategories) =>
      prevCategories.map((category) => ({
        ...category,
        posts: category.posts.map((post) =>
          post.id === postId ? { ...post, likesCount: (post.likesCount || 0) + 1 } : post
        ),
      }))
    );
    localStorage.setItem('likes', JSON.stringify({ ...likes, [postId]: (likes[postId] || 0) + 1 }));
  };

  const handleDislike = (postId) => {
    setDislikes((prev) => ({
      ...prev,
      [postId]: (prev[postId] || 0) + 1,
    }));
    setCategories((prevCategories) =>
      prevCategories.map((category) => ({
        ...category,
        posts: category.posts.map((post) =>
          post.id === postId ? { ...post, dislikesCount: (post.dislikesCount || 0) + 1 } : post
        ),
      }))
    );
  };

  const handleSubscribe = (postId) => {
    setSubscriptions((prev) => ({
      ...prev,
      [postId]: !prev[postId], // Toggle subscription
    }));
  };

  const handleCommentSubmit = (postId) => {
    const commentBody = newComment[postId] || '';
    if (!commentBody.trim()) return;

    const newCommentObj = {
      id: Date.now(), // Simple ID for frontend-only
      body: commentBody,
      user_id: 'user', // Placeholder user ID
      created_at: new Date().toISOString(),
    };

    setComments((prev) => ({
      ...prev,
      [postId]: [...(prev[postId] || []), newCommentObj],
    }));
    setNewComment((prev) => ({ ...prev, [postId]: '' }));
    localStorage.setItem('comments', JSON.stringify({ ...comments, [postId]: [...(comments[postId] || []), newCommentObj] }));
  };

  const closeModal = () => setSelectedPost(null);

  // Filter posts based on search term
  const filteredCategories = categories.map((category) => ({
    ...category,
    posts: category.posts.filter((post) =>
      post.title.toLowerCase().includes(searchTerm.toLowerCase())
    ),
  }));

  return (
    <div className="categories-wrapper">
      <Navbar />
      <header className="categories-header">
        <h1>Categories</h1>
        <p>Dive into curated content by your favorite tech domains</p>
        <div className="search-bar">
          <input
            type="text"
            placeholder="Search Categories..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <FontAwesomeIcon icon={faSearch} className="search-icon" />
        </div>
      </header>

      <div className="wrap">
        {filteredCategories.length > 0 ? (
          filteredCategories.map((category, index) => (
            <div className="category-section" key={category.id}>
              <h3 className="category-title">{category.name}</h3>
              <div className="cards-row-wrapper">
                <button className="chevron-btn left" onClick={() => scrollRow('left', index)}>
                  <FontAwesomeIcon icon={faChevronRight} rotation={180} />
                </button>
                <div className="cards-row">
                  {category.posts.map((post) => (
                    <div className="category-card" key={post.id}>
                      <h4 className="post-title">{post.title}</h4>
                      <p className="post-meta">{new Date(post.date).toLocaleDateString()}</p>
                      <div className="post-stats">
                        <span>
                          {(likes[post.id] || post.likesCount || 0)} likes{' '}
                          <FontAwesomeIcon
                            icon={faThumbsUp}
                            onClick={() => handleLike(post.id)}
                            style={{
                              cursor: hasLiked[post.id] ? 'not-allowed' : 'pointer',
                              color: hasLiked[post.id] ? 'lightgray' : 'gray',
                            }}
                          />
                        </span>
                        {post.type === 'video' && (
                          <span>
                            {(dislikes[post.id] || post.dislikesCount || 0)} dislikes{' '}
                            <FontAwesomeIcon
                              icon={faThumbsDown}
                              onClick={() => handleDislike(post.id)}
                              style={{ cursor: 'pointer', color: 'gray' }}
                            />
                          </span>
                        )}
                        <span>
                          {(comments[post.id] || []).length} comments <FontAwesomeIcon icon={faComment} />
                        </span>
                      </div>
                      <div className="post-actions">
                        <button className={`btn ${post.type}`} onClick={() => setSelectedPost(post)}>
                          {getCTA(post.type)}
                        </button>
                        <button
                          className="like-btn"
                          onClick={() => handleLike(post.id)}
                          disabled={hasLiked[post.id]}
                        >
                          Like
                        </button>
                        {post.type === 'video' && (
                          <button
                            className="subscribe-btn"
                            onClick={() => handleSubscribe(post.id)}
                          >
                            <FontAwesomeIcon
                              icon={subscriptions[post.id] ? faBellSlash : faBell}
                            />
                            {subscriptions[post.id] ? ' Unsubscribe' : ' Subscribe'}
                          </button>
                        )}
                      </div>
                      <div className="comment-section">
                        <input
                          type="text"
                          placeholder="Add a comment..."
                          value={newComment[post.id] || ''}
                          onChange={(e) =>
                            setNewComment((prev) => ({ ...prev, [post.id]: e.target.value }))
                          }
                          onKeyPress={(e) => e.key === 'Enter' && handleCommentSubmit(post.id)}
                        />
                        <div className="comments-list">
                          {(comments[post.id] || []).map((comment) => (
                            <p key={comment.id}>{comment.body}</p>
                          ))}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                <button className="chevron-btn right" onClick={() => scrollRow('right', index)}>
                  <FontAwesomeIcon icon={faChevronRight} />
                </button>
              </div>
            </div>
          ))
        ) : (
          <p>{error || 'No matching posts found.'}</p>
        )}
      </div>
      {selectedPost && (
        <div className="modal" onClick={closeModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button className="close-btn" onClick={closeModal}>
              <FontAwesomeIcon icon={faTimes} />
            </button>
            <h3>{selectedPost.title}</h3>
            {selectedPost.type === 'video' && selectedPost.url && (
              isYouTubeUrl(selectedPost.url) ? (
                <iframe
                  width="600"
                  height="338"
                  src={`https://www.youtube.com/embed/${getYouTubeVideoId(selectedPost.url)}`}
                  title={selectedPost.title}
                  frameBorder="0"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowFullScreen
                ></iframe>
              ) : (
                <p>
                  <a href={selectedPost.url} target="_blank" rel="noopener noreferrer">
                    Watch the video here
                  </a>
                </p>
              )
            )}
            {selectedPost.type === 'article' && selectedPost.url && (
              <div className="article-content">
                <p>
                  <strong>{selectedPost.title}</strong> by {selectedPost.author}.
                </p>
                <p>{selectedPost.description}</p>
                <p>
                  <a href={selectedPost.url} target="_blank" rel="noopener noreferrer">
                    Read the full article
                  </a>
                </p>
              </div>
            )}
          </div>
        </div>
      )}
      <Footer />
    </div>
  );
};

export default Categories;
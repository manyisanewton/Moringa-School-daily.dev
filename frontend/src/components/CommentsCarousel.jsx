import React, { useState, useEffect } from "react";
import "./CommentsCarousel.css";
import { getComments } from "../api";

const CommentsCarousel = () => {
  const [comments, setComments] = useState([]);
  const [current, setCurrent] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchComments = async () => {
      try {
        // Placeholder content ID; replace with dynamic ID if available
        const contentId = 1;
        const { data } = await getComments(contentId);
        setComments(Array.isArray(data) ? data : []);
      } catch (err) {
        setError('Failed to load comments' + (err.response?.status === 404 ? ': Content not found' : ''));
      } finally {
        setLoading(false);
      }
    };
    fetchComments();
  }, []);

  const prev = () => setCurrent((prev) => (prev - 1 + comments.length) % comments.length);
  const next = () => setCurrent((prev) => (prev + 1) % comments.length);

  if (loading) return <div>Loading comments...</div>;
  if (error) return <div className="error">{error}</div>;
  if (!comments.length) return <div>No comments available</div>;

  return (
    <div className="carousel">
      <h2 className="carousel-title">Comments</h2>
      <div className="carousel-content">
        <button onClick={prev} className="arrow">⟨</button>
        <div className="testimonial">
          <p className="text">"{comments[current].body}"</p>
          <span className="author">By: User {comments[current].user_id}</span>
        </div>
        <button onClick={next} className="arrow">⟩</button>
      </div>
    </div>
  );
};

export default CommentsCarousel;
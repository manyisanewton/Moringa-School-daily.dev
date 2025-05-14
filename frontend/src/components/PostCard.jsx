import React from "react";
import './PostCard.css';

const PostCard = ({ post }) => {
    return (
        <div className="post-card">
            <h3>{post.title}</h3>
            <span className="category">{post.category}</span>
            <p>{post.description}</p>
            <button className={`post-btn ${post.type.toLowerCase()}`}>
                {post.type === 'Video' ? 'Watch Now' :
                post.type === 'Article' ? 'Read Article' :
                post.type === 'Audio' ? 'Listen Now' : 'View'}
            </button>
        </div>
    );
};

export default PostCard;
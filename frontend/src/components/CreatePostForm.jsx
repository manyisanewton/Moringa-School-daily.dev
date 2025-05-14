import React, { useState, useEffect, useRef } from "react";
import "./CreatePostForm.css";
import { FaUpload } from "react-icons/fa";

const CreatePostForm = () => {
  const [formData, setFormData] = useState({
    title: "",
    category_id: null,
    description: "",
    file: null,
    media_url: null,
    contentId: null,
  });
  const [pendingPosts, setPendingPosts] = useState([]);
  const [editingPostId, setEditingPostId] = useState(null);
  const [error, setError] = useState("");
  const [status, setStatus] = useState("Pending");
  const fileInputRef = useRef(null);

  // Static categories (since we're not using a backend)
  const categories = [
    { id: 1, name: "Fullstack Development" },
    { id: 2, name: "Cyber Security" },
  ];

  // Load pending posts from localStorage on mount
  useEffect(() => {
    const storedPosts = JSON.parse(localStorage.getItem('pendingPosts') || '[]');
    setPendingPosts(storedPosts);
  }, []);

  const handleChange = (e) => {
    const { name, value, files } = e.target;
    if (name === "file") {
      const file = files[0];
      if (file) {
        // Convert file to base64 for local storage
        const reader = new FileReader();
        reader.onloadend = () => {
          setFormData({ ...formData, file: file, media_url: reader.result });
        };
        reader.readAsDataURL(file);
      }
    } else if (name === "category_id") {
      setFormData({ ...formData, [name]: value ? parseInt(value) : null });
    } else {
      setFormData({ ...formData, [name]: value });
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.category_id) {
      setError("Please select a category.");
      return;
    }
    if (!formData.title || !formData.description) {
      setError("Title and description are required.");
      return;
    }
    setError("");

    const newPost = {
      id: editingPostId || Date.now(), // Use existing ID if editing, otherwise generate new
      title: formData.title,
      body: formData.description,
      media_url: formData.media_url || null,
      content_type: formData.media_url ? "Video" : "Article",
      status: "Pending",
      category_id: formData.category_id,
      category_name: categories.find(cat => cat.id === formData.category_id)?.name || "Unknown",
    };

    let updatedPosts;
    if (editingPostId) {
      // Update existing post
      updatedPosts = pendingPosts.map(post =>
        post.id === editingPostId ? newPost : post
      );
      setEditingPostId(null);
    } else {
      // Add new post
      updatedPosts = [...pendingPosts, newPost];
    }

    setPendingPosts(updatedPosts);
    localStorage.setItem('pendingPosts', JSON.stringify(updatedPosts));
    setFormData({
      title: "",
      category_id: null,
      description: "",
      file: null,
      media_url: null,
      contentId: null,
    });
    setStatus("Pending");
  };

  const handleEdit = (post) => {
    setFormData({
      title: post.title,
      category_id: post.category_id,
      description: post.body,
      file: null,
      media_url: post.media_url,
      contentId: post.id,
    });
    setEditingPostId(post.id);
    setStatus("Pending");
  };

  const handleUploadAreaClick = () => {
    fileInputRef.current.click();
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.currentTarget.classList.add('drag-over');
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.currentTarget.classList.remove('drag-over');
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.currentTarget.classList.remove('drag-over');
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      const file = files[0];
      const reader = new FileReader();
      reader.onloadend = () => {
        setFormData({ ...formData, file: file, media_url: reader.result });
      };
      reader.readAsDataURL(file);
    }
  };

  return (
    <div className="create-post">
      <h2>{editingPostId ? "Edit Post" : "Create Post"}</h2>
      <p>Share something with the community</p>
      <form className="post-form" onSubmit={handleSubmit}>
        <label>Title:</label>
        <input
          type="text"
          name="title"
          placeholder="Title"
          value={formData.title}
          onChange={handleChange}
          required
        />

        <label>Category:</label>
        <select
          name="category_id"
          value={formData.category_id || ""}
          onChange={handleChange}
          required
        >
          <option value="">Select a category</option>
          {categories.map((cat) => (
            <option key={cat.id} value={cat.id}>{cat.name}</option>
          ))}
        </select>

        <label>Description:</label>
        <textarea
          name="description"
          placeholder="Write the Description"
          value={formData.description}
          onChange={handleChange}
          required
        ></textarea>

        <label>Upload a File (Video or Image):</label>
        <div className="file-upload">
          <div
            className="upload-area"
            onClick={handleUploadAreaClick}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <FaUpload className="upload-icon" />
            <p>
              {formData.file?.name || formData.media_url ? "File selected" : "Choose a file or drag & drop it here!"}
              <br />
              JPEG, PNG, MP4 formats, up to 50 MB.
            </p>
            {formData.media_url && (
              <div className="media-preview">
                {formData.media_url.startsWith('data:image/') ? (
                  <img src={formData.media_url} alt="Preview" style={{ maxWidth: '100px', maxHeight: '100px' }} />
                ) : formData.media_url.startsWith('data:video/') ? (
                  <video src={formData.media_url} controls style={{ maxWidth: '100px', maxHeight: '100px' }} />
                ) : null}
              </div>
            )}
            <input
              id="file-upload"
              type="file"
              name="file"
              accept="image/jpeg,image/png,video/mp4"
              onChange={handleChange}
              ref={fileInputRef}
              style={{ display: "none" }}
            />
          </div>
        </div>

        <button
          type="submit"
          disabled={!formData.title || !formData.description || !formData.category_id}
        >
          {editingPostId ? "Update Post" : "Submit for Approval"}
        </button>
        {error && <p className="error">{error}</p>}
      </form>

      <div className="pending-posts">
        <h3>Pending Posts</h3>
        {pendingPosts.length > 0 ? (
          <div className="posts-list">
            {pendingPosts.map(post => (
              <div key={post.id} className="post-item">
                <h4>{post.title}</h4>
                <p><strong>Category:</strong> {post.category_name}</p>
                <p><strong>Description:</strong> {post.body}</p>
                {post.media_url && (
                  <div className="media-preview">
                    {post.media_url.startsWith('data:image/') ? (
                      <img src={post.media_url} alt={post.title} style={{ maxWidth: '100px', maxHeight: '100px' }} />
                    ) : post.media_url.startsWith('data:video/') ? (
                      <video src={post.media_url} controls style={{ maxWidth: '100px', maxHeight: '100px' }} />
                    ) : null}
                  </div>
                )}
                <p><strong>Status:</strong> {post.status}</p>
                <button
                  className="edit-btn"
                  onClick={() => handleEdit(post)}
                >
                  Edit
                </button>
              </div>
            ))}
          </div>
        ) : (
          <p>No pending posts.</p>
        )}
      </div>
    </div>
  );
};

export default CreatePostForm;
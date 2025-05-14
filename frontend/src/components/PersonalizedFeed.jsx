import React, { useState, useEffect } from "react";
import { Swiper, SwiperSlide } from "swiper/react";
import "swiper/css";
import "swiper/css/pagination";
import "./PersonalizedFeed.css";
import { Pagination } from "swiper/modules";
import PostCard from "./PostCard";
import api from "../api";

const PersonalizedFeed = () => {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchContent = async () => {
      try {
        const response = await api.get("/content", {
          params: { page: 1, per_page: 10 },
        });
        // Set posts to response.data.items, which is the array of posts
        setPosts(response.data.items || []);
      } catch (err) {
        setError("Failed to load feed. Please try again.");
        console.error("Error fetching content:", err.response?.data || err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchContent();
  }, []);

  // Fetch category and author details for each post
  useEffect(() => {
    const enrichPosts = async () => {
      const enrichedPosts = await Promise.all(
        posts.map(async (post) => {
          try {
            // Fetch category name
            const categoryResponse = await api.get(`/categories/${post.category_id}`);
            const categoryName = categoryResponse.data.name || "Unknown";

            // Fetch author name
            const authorResponse = await api.get(`/auth/me`); // Adjust endpoint if needed
            const authorName = authorResponse.data.name || "Unknown";

            return {
              ...post,
              category: categoryName,
              author: authorName,
            };
          } catch (err) {
            console.error(`Error enriching post ${post.id}:`, err);
            return {
              ...post,
              category: "Unknown",
              author: "Unknown",
            };
          }
        })
      );
      setPosts(enrichedPosts);
    };

    if (posts.length > 0 && !posts[0].category) {
      enrichPosts();
    }
  }, [posts]);

  if (loading) return <p>Loading...</p>;
  if (error) return <p>{error}</p>;

  return (
    <section className="feed-section">
      <h2>Personalized Feed</h2>
      <p>Content based on your likes and interests</p>
      <Swiper
        spaceBetween={20}
        slidesPerView={1}
        breakpoints={{
          640: { slidesPerView: 2 },
          768: { slidesPerView: 3 },
          1024: { slidesPerView: 4 },
        }}
        pagination={{ clickable: true }}
        modules={[Pagination]}
      >
        {posts.map((post) => (
          <SwiperSlide key={post.id}>
            <PostCard
              post={{
                id: post.id,
                title: post.title,
                category: post.category || "Loading...",
                description: post.body || "",
                file: post.media_url || "",
                author: post.author || "Loading...",
                date: post.created_at,
                type: post.content_type,
              }}
            />
          </SwiperSlide>
        ))}
      </Swiper>
    </section>
  );
};

export default PersonalizedFeed;
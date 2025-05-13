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
        setPosts(response.data);
      } catch (err) {
        setError("Failed to load feed. Please try again.");
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchContent();
  }, []);

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
                category: post.category_id
                  ? api.get(`/categories/${post.category_id}`).then((res) => res.data.name)
                  : "Unknown",
                description: post.body,
                file: post.media_url || "",
                author: post.author_id
                  ? api.get(`/auth/me`).then((res) => res.data.name)
                  : "Unknown",
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
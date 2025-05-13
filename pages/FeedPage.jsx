import Navbar from "../components/Navbar/UserNavbar";
import CreatePostForm from "../components/CreatePostForm";
import PersonalizedFeed from "../components/PersonalizedFeed";
import Footer from "../components/Footer";
import { useNavigate } from "react-router-dom";
import { useEffect } from "react";

const FeedPage = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      navigate("/login");
    }
  }, [navigate]);

  return (
    <div>
      <Navbar />
      <CreatePostForm />
      <PersonalizedFeed />
      <Footer />
    </div>
  );
};

export default FeedPage;
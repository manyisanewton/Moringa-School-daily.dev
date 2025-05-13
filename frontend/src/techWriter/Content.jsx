import React, { useState, useEffect } from "react";
import axios from 'axios';
import Navbar from "../components/Navbar/TechNavbar";
import FilterToolbar from "../components/FilterToolbar";
import ContentTable from "../components/ContentTable";
import Footer from "../components/Footer";
import './Content.css';

const Content = () => {
    const [contents, setContents] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchContents = async () => {
            try {
                const userResponse = await axios.get('http://localhost:5000/auth/me', {
                    headers: {
                        Authorization: `Bearer ${localStorage.getItem('access_token')}`
                    }
                });
                const userId = userResponse.data.id;

                const contentResponse = await axios.get(`http://localhost:5000/content?user_id=${userId}`, {
                    headers: {
                        Authorization: `Bearer ${localStorage.getItem('access_token')}`
                    }
                });
                setContents(contentResponse.data.items);
                setLoading(false);
            } catch (error) {
                console.error('Error fetching content:', error);
                setLoading(false);
            }
        };
        fetchContents();
    }, []);

    return (
        <div>
            <Navbar />
            <div className="contentContainer">
                <div className="content-greeting">
                    <h1 className="content-head">My Content</h1>
                    <p className="content-description">View, edit and track the performance of your post</p>
                </div>
                <FilterToolbar />
                {loading ? <p>Loading...</p> : <ContentTable contents={contents} />}
            </div>
            <Footer />
        </div>
    );
};

export default Content;
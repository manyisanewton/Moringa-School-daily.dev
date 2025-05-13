import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./Code.css";
import logo from "../assets/logo.png";
import { verifyResetCode } from "../api";

function Code() {
    const [code, setCode] = useState("");
    const [email, setEmail] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        const storedEmail = localStorage.getItem("resetEmail");
        if (!storedEmail) {
            navigate("/forgot-password");
        } else {
            setEmail(storedEmail);
        }
    }, [navigate]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError("");
        setLoading(true);

        try {
            await verifyResetCode(email, code);
            localStorage.setItem("resetCode", code);
            setLoading(false);
            navigate("/new-password");
        } catch (err) {
            setLoading(false);
            setError(err.response?.data?.error || "Invalid or expired code. Please try again.");
        }
    };

    const handleBack = () => {
        localStorage.removeItem("resetEmail");
        navigate("/forgot-password");
    };

    return (
        <div className="new-code-container">
            <div className="logo-section">
                <img className="light-logo" src={logo} alt="Moringa School daily.dev logo" />
            </div>
            <div className="code-form">
                <h2>We sent you a code</h2>
                <p>Check your email to get your confirmation code. If you need to request a new code, go back and re-enter your email.</p>
                {error && <p className="error">{error}</p>}
                <form onSubmit={handleSubmit}>
                    <input
                        type="text"
                        placeholder="Enter your code"
                        className="code-input"
                        value={code}
                        onChange={(e) => setCode(e.target.value)}
                        maxLength={6}
                        required
                    />
                    <div className="code-buttons">
                        <button type="button" className="back-button" onClick={handleBack} disabled={loading}>
                            Back
                        </button>
                        <button type="submit" className="next-button" disabled={loading}>
                            {loading ? "Verifying..." : "Next"}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}

export default Code;
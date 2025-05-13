import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./ResetPasswordPage.css";
import darklogo from "../assets/dark-logo.png";
import { requestPasswordReset } from "../api";

function ResetPassword() {
    const [email, setEmail] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError("");
        setLoading(true);

        try {
            await requestPasswordReset(email);
            localStorage.setItem("resetEmail", email);
            setLoading(false);
            navigate("/code");
        } catch (err) {
            setLoading(false);
            setError(err.response?.data?.error?.identifier?.[0] || "Failed to send reset code. Please try again.");
        }
    };

    return (
        <div className="reset-password-container">
            <div className="logo-section">
                <img className="logo" src={darklogo} alt="The dark Moringa School daily.dev logo" />
            </div>
            <div className="reset-password-form">
                <h2>Reset your Password</h2>
                <p>Enter the email associated with your account to change your password.</p>
                {error && <p className="error">{error}</p>}
                <form onSubmit={handleSubmit}>
                    <input
                        type="email"
                        placeholder="Enter your email"
                        className="email-input"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                    />
                    <button type="submit" className="reset-password-button" disabled={loading}>
                        {loading ? "Sending..." : "Next"}
                    </button>
                </form>
            </div>
        </div>
    );
}

export default ResetPassword;
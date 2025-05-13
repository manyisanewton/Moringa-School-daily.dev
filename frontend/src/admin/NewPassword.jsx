import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./NewPassword.css";
import darklogo from "../assets/dark-logo.png";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faEye, faEyeSlash } from "@fortawesome/free-solid-svg-icons";
import { resetPassword } from "../api";

function NewPassword() {
    const [newPassword, setNewPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [showPassword, setShowPassword] = useState(false);
    const [showConfirmPassword, setShowConfirmPassword] = useState(false);
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        if (!localStorage.getItem("resetCode")) {
            navigate("/forgot-password");
        }
    }, [navigate]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError("");
        setLoading(true);

        const code = localStorage.getItem("resetCode");
        try {
            await resetPassword(code, newPassword, confirmPassword);
            localStorage.removeItem("resetEmail");
            localStorage.removeItem("resetCode");
            setLoading(false);
            navigate("/login");
        } catch (err) {
            setLoading(false);
            setError(err.response?.data?.error || "Failed to reset password. Please try again.");
        }
    };

    return (
        <div className="new-password-container">
            <div className="logo-section">
                <img className="logo-new" src={darklogo} alt="Moringa School daily.dev logo" />
            </div>
            <div className="new-password-form">
                <h2>Choose your new Password</h2>
                <p>Make sure your new password is 8 characters or more. Try including numbers, letters, or punctuation marks for a <span>strong password</span></p>
                {error && <p className="error">{error}</p>}
                <form onSubmit={handleSubmit}>
                    <div className="password-wrapper">
                        <input
                            type={showPassword ? 'text' : 'password'}
                            placeholder="Enter your New Password"
                            value={newPassword}
                            onChange={(e) => setNewPassword(e.target.value)}
                            required
                        />
                        <FontAwesomeIcon
                            icon={showPassword ? faEyeSlash : faEye}
                            className="eye-icon"
                            onClick={() => setShowPassword(!showPassword)}
                        />
                    </div>
                    <div className="password-wrapper">
                        <input
                            type={showConfirmPassword ? 'text' : 'password'}
                            placeholder="Confirm your New Password"
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                            required
                        />
                        <FontAwesomeIcon
                            icon={showConfirmPassword ? faEyeSlash : faEye}
                            className="eye-icon"
                            onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                        />
                    </div>
                    <button type="submit" className="change-password" disabled={loading}>
                        {loading ? "Changing..." : "Change Password"}
                    </button>
                </form>
            </div>
        </div>
    );
}

export default NewPassword;
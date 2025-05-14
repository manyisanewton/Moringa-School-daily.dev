import React, { Component } from "react";
import { useNavigate } from "react-router-dom";

// Functional component to use hooks within ErrorBoundary
const NavigateWrapper = ({ children }) => {
    return children;
};

// Class-based ErrorBoundary
class ErrorBoundary extends Component {
    state = { hasError: false };

    static getDerivedStateFromError() {
        return { hasError: true };
    }

    componentDidCatch(error, errorInfo) {
        console.error("ErrorBoundary caught an error:", error, errorInfo);
    }

    render() {
        if (this.state.hasError) {
            return (
                <NavigateWrapper>
                    <div className="error-boundary">
                        <h2>Something went wrong</h2>
                        <p>Please try again or return to the login page.</p>
                        <button onClick={() => window.location.href = "/login"}>
                            Go to Login
                        </button>
                    </div>
                </NavigateWrapper>
            );
        }
        return this.props.children;
    }
}

export default ErrorBoundary;
import React from 'react';
import './LandingPage.css';
import heroImage from '../assets/hero-image.jpeg';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faPlay } from '@fortawesome/free-solid-svg-icons';

function LandingPage() {
    // redirect to registration page
    const handleJoinNow = () => {
        window.location.href = '/register';
    };

    // redirect to login page
    const handleLogIn = () => {
        window.location.href = '/login';
    };

    return (
        <div className='landing-container'>
            <div className='landing-content'>
                <div className='landing-text'>
                    <h1>
                        Explore <span className='highlighted-content'>Verified Tech Wisdom</span> from the Moringa Community
                    </h1>
                    <p className='subtitle'>
                        Watch, read, and listen to curated content from industry experts, alumni, and your peers
                    </p>
            
                    <div className='button-group'>
                        <button className='join-button' onClick={handleJoinNow}>Join Now</button>
                        <button className='login-button' onClick={handleLogIn}>Log In</button>
                    </div>
                </div>
        
                <div className='landing-image'>
                    <img src={heroImage} alt="A woman coding" className='hero-image' style={{ width: '100%', height: '800px'}}/>
                    <div className='play-button-overlay'>
                        <div className='play-button'>
                            <FontAwesomeIcon icon={faPlay} className='play-icon' />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default LandingPage;

## Moringa School daily.dev
### A Verified Tech Learning & Community Platform

# 📌 Table of Contents
## .Project Overview

## . MVP Features

## .Admin Features

# #.Tech Writer Features

## .User Features

# #.Technical Stack

## .Installation & Setup

## .API Endpoints

## .Database Schema

## .Testing

## .Future Roadmap

## .Contributing

## .License

## 🌐 Project Overview
Moringa School daily.dev is a platform designed to create an open and accessible community for Moringa School students, alumni, and instructors to share verified tech content. This includes insightful articles, educational videos, and podcasts that cover various aspects of the tech industry.

The content is created by members of the Moringa School community, including alumni who have hands-on industry experience, instructors who provide mentorship, and guest experts from the broader tech world.

The platform aims to offer an inclusive and collaborative space for learning and sharing experiences, all while ensuring that the content provided is verified and reliable. By focusing on industry-related topics, this platform serves as a bridge between Moringa School students and the wider tech community, fostering growth, mentorship, and peer learning.
## 🚀 Key Goals:
Provide Trusted, Structured Learning Resources: Moringa School daily.dev is aimed at offering students access to accurate, structured, and insightful resources that help with their learning journey.

Foster Peer Discussions & Mentorship: The platform encourages a community where students and professionals can engage in meaningful discussions, exchange ideas, and mentor each other.

Enable Personalized Content Discovery: By leveraging categories, user preferences, and notifications, the platform offers a personalized content experience. Users can easily discover the content that matters most to them, creating a tailored experience.

## ✨ MVP Features

## 👑 Admin Features
Admins hold the highest level of control on the platform and have the responsibility of overseeing content, managing users, and ensuring the platform’s guidelines are followed.

User Management:

Add New Users: Admins can register new users (Tech Writers, Students) into the platform, granting them the appropriate role based on their purpose.

Deactivate Accounts: If a user violates platform policies or becomes inactive, admins have the ability to deactivate their account to ensure the platform remains safe and adheres to the guidelines.

Content Moderation:

Approve or Reject Content: Before content goes live on the platform, admins have the power to approve or reject submissions to ensure they meet the platform's quality standards.

Remove Flagged Content: Admins can remove content flagged by other users or tech writers for inappropriate material or violations of community guidelines.

Category Management:

Organize Content by Topics: Admins are able to create and manage categories to classify content. Categories may include topics such as "Web Development," "Data Science," and "Software Engineering."

## ✍️ Tech Writer Features
Tech Writers play a crucial role in providing valuable content to the platform. They create educational materials, engage with the community, and moderate content.

Profile & Content Creation:

Write and Publish Content: Tech Writers can create posts that include articles, videos, and podcasts, sharing knowledge on various tech-related topics.

Edit and Update Posts: After content is submitted, Tech Writers can edit their posts, making corrections or additions to keep content relevant.

Community Moderation:

Flag Inappropriate Content: Tech Writers can flag content submitted by others that violates platform guidelines or does not meet the quality standards.

Approve Posts for Publication: Tech Writers have a say in which content gets published publicly, ensuring that only verified and high-quality content is showcased.

Engagement:

Like/Dislike and Comment on Posts: Tech Writers can interact with other users’ content by liking, disliking, and commenting on posts, fostering further community engagement.

## 👥 User Features
Users are the learners and community members who benefit from the content shared by Tech Writers and engage in peer discussions.

-Personalized Feed:

Subscribe to Categories: Users can subscribe to specific categories like "AI," "Web Development," or "Cybersecurity," tailoring the content they receive to their interests.

Save to Wishlist: Users can add content they find interesting to their wishlist for future viewing or reading.

-Social Interaction:

Comment, Reply, and Vote: Users can engage with posts by commenting, replying to other comments, and participating in Reddit-style thread discussions. They can also vote on content (like/dislike).

Engage in Threaded Conversations: Users can start or reply to threads, providing a more dynamic conversation structure.

-Notifications:

Real-time Content Updates: Users receive notifications whenever new content is posted in their subscribed categories, keeping them up to date with the latest developments.

## 🖥️ Technical Stack
### Backend:
Python (Flask): Flask is used to handle API routes, database connections, and user authentication. It provides a simple and flexible way to build scalable and maintainable web applications.

PostgreSQL: This relational database is used to store and manage data for users, content, comments, and categories. PostgreSQL ensures data consistency, scalability, and robustness.

### Frontend:
React.js: React.js is the core framework used to build the frontend of the application. It provides a dynamic and interactive user interface that is both efficient and scalable.

Redux Toolkit: Redux is used to manage the application's state, ensuring that data flows seamlessly between components, especially for managing user preferences, subscriptions, and notifications.

### Testing Frameworks:
Jest: Jest is a testing framework used for frontend testing, ensuring the React components behave as expected.

Minitests: Minitests are used for testing the backend API to ensure that the system functions as expected, validating everything from user authentication to content submission.

### Wireframes:
Figma: The platform’s UI/UX wireframes were designed in Figma, offering a clean and intuitive layout. Figma allowed  the team to collaborate on designing a responsive, mobile-friendly experience.

## 🛠️ Installation & Setup
### ⚛️ Frontend Setup:
1. Clone the repository:

git clone https://github.com/your-username/moringa-school-daily-dev.git

2. Navigate to the frontend directory:
cd moringa-school-daily-dev/frontend

3. Install the necessary dependencies:
npm install

4. Start the frontend server:
npm start

Visit http://localhost(the respective port)to see the app running.

#### 🐍 Backend Setup:
1. Clone the repository:
git clone https://github.com/your-username/moringa-school-daily-dev.git

2. Navigate to the backend directory:
cd moringa-school-daily-dev/backend
python3 -m venv venv
source venv/bin/activate


3. Install backend dependencies:
pip install -r requirements.txt

4. Set up the PostgreSQL database:
python manage.py db upgrade
5. Start the backend server:
python app.py
-Visit the given  http://localhost: to access the backend.

### 🔌 API Endpoints
The platform follows RESTful principles to allow communication between the frontend and backend.

### User Authentication:
POST /auth/register: Register a new user.

POST /auth/login: User login and authentication.

### Content Management:
GET /content: Fetch all published content.

POST /content: Submit new content (article, video, podcast).

PATCH /content/{id}: Edit existing content.

DELETE /content/{id}: Delete a post.

### Commenting System:
POST /comments: Add a new comment to a post.

GET /comments/{contentId}: Fetch all comments related to a specific post.

## 🗄️ Database Schema
-The platform’s database is organized into several tables, including:

-Users: Stores information like name, email, and role (admin, tech writer, user).

-Content: Stores articles, videos, podcasts, including metadata such as type, title, description, and the author.

-Comments: Stores comments and replies, allowing users to engage with content.

-Categories: Organizes content into categories such as “Web Development,” “AI,” and “Data Science.”

## ✅ Testing
Testing is critical to ensure the platform works smoothly:

Frontend Testing: Jest is used to test React components and ensure they render correctly and interact as expected.

Backend Testing: Minitests are used to ensure the backend API behaves correctly, including data fetching, user authentication, and content management.

## 📈 Future Roadmap
-The platform will continue to evolve with the following features:

-Content Recommendation Engine: Based on user activity and preferences, content suggestions will be provided to enhance the learning experience.

-Search Functionality: Allow users to search for specific articles, videos, and podcasts.

-Mobile Application: Develop a dedicated mobile app for users to access content on the go.

## 🛠️ Contributing
We welcome contributions to make our  Moringa School daily.dev better! To contribute:

-Fork the repository.

-Create a new branch for your feature or bug fix.

-Implement your changes and add tests.

-Submit a pull request with a detailed explanation of your changes.

📝 License
This project is licensed under the MIT License 

## Authors
1. Newton manyisa-newton.manyisa@student.moringaschool.com
2. Shakira Syevuo-shakira.syevuo@student.moringaschool.com
3. Sandra Misigo-sandra.misigo@student.moringaschool.com
4. Patrick Shawukie-kawuki.patrick@student.moringaschool.com
5. Joyce Ngari-joyce.ngari@student.moringaschool.com







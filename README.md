src/
  ├── assets/                   # Static assets (images, icons, etc.)
  │   ├── logo.png
  │   └── icons/
  ├── components/               # Reusable UI components
  │   ├── Navbar.jsx
  │   ├── NotificationCard.jsx
  │   ├── ContentCard.jsx
  │   ├── CategoryCard.jsx
  │   └── FormInput.jsx
  ├── pages/                    # Page components (each page from Figma)
  │   ├── Home.jsx             # Landing page ("Explore Verified Tech Wisdom")
  │   ├── Login.jsx            # Login page
  │   ├── Register.jsx         # Register page
  │   ├── Dashboard.jsx        # User dashboard ("Welcome Back, User")
  │   ├── AdminDashboard.jsx   # Admin dashboard ("Welcome, Admin")
  │   ├── Feed.jsx             # Feed page ("Hello, User" with notifications and feed)
  │   ├── Notifications.jsx    # Notifications page
  │   ├── Profile.jsx          # Profile page
  │   ├── ContentCreate.jsx    # Create New Content page
  │   ├── MyContent.jsx        # My Content page
  │   ├── ContentManagement.jsx # Content Management page (Admin)
  │   ├── FlaggedContent.jsx   # Flagged Content page (Admin)
  │   ├── CategoryManagement.jsx # Category Management page (Admin)
  │   ├── UserManagement.jsx   # User Management page (Admin)
  │   └── Categories.jsx       # Categories page
  ├── hooks/                   # Custom hooks
  │   ├── useAuth.js
  │   └── useContent.js
  ├── redux/                   # Redux store and slices
  │   ├── slices/
  │   │   ├── authSlice.js
  │   │   └── contentSlice.js
  │   └── store.js
  ├── utils/                   # Utility functions and API setup
  │   ├── api.js
  │   └── constants.js
  ├── styles/                  # Global styles and Tailwind config
  │   ├── App.css
  │   └── tailwind.css
  ├── App.jsx                  # Main app component with routing
  ├── main.jsx                 # Entry point
  └── index.html
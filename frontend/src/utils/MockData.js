const mockData = {
    users: [
      { id: 1, name: 'John Doe', email: 'john@example.com', role: 'User', active: true },
      { id: 2, name: 'Jane Smith', email: 'jane@example.com', role: 'Tech Writer', active: true },
      { id: 3, name: 'Admin User', email: 'admin@example.com', role: 'Admin', active: true },
    ],
    content: [
      { id: 1, type: 'Article', title: 'Intro to DevOps', author: 'Jane Smith', category: 'DevOps', description: 'An introduction to DevOps practices', status: 'Flagged', fileName: 'intro_devops.pdf', reason: 'Inappropriate language', stats: { likes: 50, shares: 0, comments: 5 } },
      { id: 2, type: 'Video', title: 'React Hooks Deep Dive', author: 'Jane Smith', category: 'React', description: 'A deep dive into React Hooks', status: 'Published', fileName: 'react_hooks.mp4', stats: { likes: 50, shares: 0, comments: 5 } },
      { id: 3, type: 'Audio', title: 'Why Python is Awesome', author: 'Jane Smith', category: 'Python', description: 'Reasons to love Python', status: 'Waiting', fileName: 'python_awesome.mp3', stats: { likes: 50, shares: 0, comments: 5 } },
      { id: 4, type: 'Blog', title: 'Tech life at Moringa', author: 'Jane Smith', category: 'Tech Life', description: 'Life as a tech student at Moringa', status: 'Flagged', reason: 'Inappropriate language', stats: { likes: 50, shares: 0, comments: 5 } },
      { id: 5, type: 'Video', title: 'How to debug efficiently', author: 'Jane Smith', category: 'Debugging', description: 'Tips for efficient debugging', status: 'Flagged', reason: 'Spam', stats: { likes: 50, shares: 0, comments: 5 } },
      { id: 6, type: 'Audio', title: 'Crash course on Git', author: 'Jane Smith', category: 'Git', description: 'A quick Git crash course', status: 'Flagged', reason: 'Misleading information', stats: { likes: 50, shares: 0, comments: 5 } },
    ],
    categories: [
      { id: 1, name: 'DevOps', description: 'DevOps practices and tools', posts: 5 },
      { id: 2, name: 'React', description: 'React.js framework', posts: 3 },
      { id: 3, name: 'Python', description: 'Python programming', posts: 4 },
      { id: 4, name: 'Tech Life', description: 'Life in tech', posts: 2 },
      { id: 5, name: 'Debugging', description: 'Debugging techniques', posts: 1 },
      { id: 6, name: 'Git', description: 'Version control with Git', posts: 1 },
    ],
    recentActivity: [
      { time: '10:00 AM', event: 'New User "john@example.com" Created' },
      { time: '10:15 AM', event: 'Content "Intro to DevOps" submitted (Pending approval)' },
      { time: '10:30 AM', event: 'Category "DevOps" Created' },
    ],
    notifications: [
      { id: 1, time: '10:00 AM', event: 'Your content "Intro to DevOps" has been flagged for review', userRole: 'Tech Writer' },
      { id: 2, time: '10:15 AM', event: 'Your content "React Hooks Deep Dive" has been published', userRole: 'Tech Writer' },
      { id: 3, time: '10:30 AM', event: 'Your content "Tech life at Moringa" has been flagged: Inappropriate language', userRole: 'Tech Writer' },
    ],
  };
  
  export const fetchUsers = () => Promise.resolve(mockData.users);
  export const fetchContent = () => Promise.resolve(mockData.content);
  export const fetchCategories = () => Promise.resolve(mockData.categories);
  export const fetchRecentActivity = () => Promise.resolve(mockData.recentActivity);
  export const fetchNotifications = (role) => Promise.resolve(mockData.notifications.filter(notif => notif.userRole === role));
  
  export const addUser = (user) => {
    mockData.users.push({ id: mockData.users.length + 1, ...user, active: true });
  };
  export const updateUser = (id, updatedUser) => {
    const index = mockData.users.findIndex(user => user.id === id);
    if (index !== -1) mockData.users[index] = { ...mockData.users[index], ...updatedUser };
  };
  export const deactivateUser = (id) => {
    const index = mockData.users.findIndex(user => user.id === id);
    if (index !== -1) mockData.users[index].active = false;
  };
  export const activateUser = (id) => {
    const index = mockData.users.findIndex(user => user.id === id);
    if (index !== -1) mockData.users[index].active = true;
  };
  
  export const addCategory = (category) => {
    mockData.categories.push({ id: mockData.categories.length + 1, ...category });
  };
  export const updateCategory = (id, updatedCategory) => {
    const index = mockData.categories.findIndex(cat => cat.id === id);
    if (index !== -1) mockData.categories[index] = { ...mockData.categories[index], ...updatedCategory };
  };
  export const deleteCategory = (id) => {
    const index = mockData.categories.findIndex(cat => cat.id === id);
    if (index !== -1) mockData.categories.splice(index, 1);
  };
  
  export const addContent = (content) => {
    mockData.content.push({ id: mockData.content.length + 1, ...content, status: 'Waiting', stats: { likes: 0, shares: 0, comments: 0 } });
  };
  export const updateContent = (id, updatedContent) => {
    const index = mockData.content.findIndex(item => item.id === id);
    if (index !== -1) mockData.content[index] = { ...mockData.content[index], ...updatedContent };
  };
  export const deleteContent = (id) => {
    const index = mockData.content.findIndex(item => item.id === id);
    if (index !== -1) mockData.content.splice(index, 1);
  };
  export const flagContent = (id, reason) => {
    const index = mockData.content.findIndex(item => item.id === id);
    if (index !== -1) {
      mockData.content[index].status = 'Flagged';
      mockData.content[index].reason = reason;
      const contentTitle = mockData.content[index].title;
      addNotification(`Your content "${contentTitle}" has been flagged: ${reason}`, 'Tech Writer');
    }
  };
  
  export const addRecentActivity = (event) => {
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    mockData.recentActivity.push({ time, event });
  };
  
  export const addNotification = (event, userRole) => {
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    mockData.notifications.push({ id: mockData.notifications.length + 1, time, event, userRole });
  };
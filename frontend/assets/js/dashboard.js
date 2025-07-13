// Dashboard JavaScript
class Dashboard {
    constructor() {
        this.stats = null;
        this.recentActivity = null;
        this.progress = null;
        this.achievements = null;
        this.init();
    }

    init() {
        this.loadDashboardData();
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Profile update form
        const profileForm = document.getElementById('profileForm');
        if (profileForm) {
            profileForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.updateProfile();
            });
        }

        // Password change form
        const passwordForm = document.getElementById('passwordForm');
        if (passwordForm) {
            passwordForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.changePassword();
            });
        }

        // Tab navigation
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('tab-btn')) {
                this.showTab(e.target.dataset.tab);
            }
        });
    }

    async loadDashboardData() {
        await Promise.all([
            this.loadStats(),
            this.loadRecentActivity(),
            this.loadProgress(),
            this.loadAchievements(),
            this.loadProfile()
        ]);
    }

    async loadStats() {
        try {
            const token = localStorage.getItem('token');
            const response = await fetch('http://127.0.0.1:5000/api/dashboard/stats', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                this.stats = await response.json();
                this.displayStats();
            }
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    }

    displayStats() {
        if (!this.stats) return;

        // Update stats cards
        const statsContainer = document.getElementById('statsContainer');
        if (statsContainer) {
            statsContainer.innerHTML = `
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-icon">📚</div>
                        <div class="stat-content">
                            <h3>${this.stats.study_sessions.total}</h3>
                            <p>Study Sessions</p>
                        </div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon">🧠</div>
                        <div class="stat-content">
                            <h3>${this.stats.quizzes.total}</h3>
                            <p>Quizzes Taken</p>
                        </div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon">⭐</div>
                        <div class="stat-content">
                            <h3>${this.stats.study_sessions.avg_rating}</h3>
                            <p>Avg. Rating</p>
                        </div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon">👥</div>
                        <div class="stat-content">
                            <h3>${this.stats.groups.total}</h3>
                            <p>Study Groups</p>
                        </div>
                    </div>
                </div>
            `;
        }

        // Update user info
        const userInfoContainer = document.getElementById('userInfoContainer');
        if (userInfoContainer && this.stats.user) {
            userInfoContainer.innerHTML = `
                <div class="user-info">
                    <h2>Welcome back, ${this.stats.user.name}!</h2>
                    <p>Grade Level: ${this.stats.user.grade_level || 'Not specified'}</p>
                    <p>Subjects: ${this.stats.user.subjects.join(', ') || 'None selected'}</p>
                    <p>Member since: ${new Date(this.stats.user.joined_date).toLocaleDateString()}</p>
                </div>
            `;
        }
    }

    async loadRecentActivity() {
        try {
            const token = localStorage.getItem('token');
            const response = await fetch('http://127.0.0.1:5000/api/dashboard/recent-activity', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                this.recentActivity = await response.json();
                this.displayRecentActivity();
            }
        } catch (error) {
            console.error('Error loading recent activity:', error);
        }
    }

    displayRecentActivity() {
        if (!this.recentActivity) return;

        const activityContainer = document.getElementById('recentActivityContainer');
        if (!activityContainer) return;

        let activityHTML = '<h3>Recent Activity</h3>';

        // Combine and sort activities
        const activities = [];
        
        this.recentActivity.sessions.forEach(session => {
            activities.push({
                type: 'session',
                data: session,
                date: new Date(session.created_at)
            });
        });

        this.recentActivity.quizzes.forEach(quiz => {
            activities.push({
                type: 'quiz',
                data: quiz,
                date: new Date(quiz.started_at)
            });
        });

        activities.sort((a, b) => b.date - a.date);

        if (activities.length === 0) {
            activityHTML += '<p>No recent activity</p>';
        } else {
            activityHTML += '<div class="activity-list">';
            activities.slice(0, 5).forEach(activity => {
                if (activity.type === 'session') {
                    activityHTML += `
                        <div class="activity-item session">
                            <div class="activity-icon">📚</div>
                            <div class="activity-content">
                                <p>Study session on ${activity.data.subject}</p>
                                <small>${activity.date.toLocaleDateString()}</small>
                            </div>
                        </div>
                    `;
                } else {
                    activityHTML += `
                        <div class="activity-item quiz">
                            <div class="activity-icon">🧠</div>
                            <div class="activity-content">
                                <p>Quiz: ${activity.data.score || 0}% score</p>
                                <small>${activity.date.toLocaleDateString()}</small>
                            </div>
                        </div>
                    `;
                }
            });
            activityHTML += '</div>';
        }

        activityContainer.innerHTML = activityHTML;
    }

    async loadProgress() {
        try {
            const token = localStorage.getItem('token');
            const response = await fetch('http://127.0.0.1:5000/api/dashboard/progress', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                this.progress = await response.json();
                this.displayProgress();
            }
        } catch (error) {
            console.error('Error loading progress:', error);
        }
    }

    displayProgress() {
        if (!this.progress) return;

        const progressContainer = document.getElementById('progressContainer');
        if (!progressContainer) return;

        let progressHTML = '<h3>Learning Progress</h3>';

        if (Object.keys(this.progress.progress).length === 0) {
            progressHTML += '<p>No progress data available</p>';
        } else {
            progressHTML += '<div class="progress-grid">';
            Object.entries(this.progress.progress).forEach(([subject, data]) => {
                progressHTML += `
                    <div class="progress-card">
                        <h4>${subject}</h4>
                        <div class="progress-stats">
                            <div class="progress-stat">
                                <span class="stat-label">Sessions:</span>
                                <span class="stat-value">${data.sessions}</span>
                            </div>
                            <div class="progress-stat">
                                <span class="stat-label">Questions:</span>
                                <span class="stat-value">${data.questions}</span>
                            </div>
                            <div class="progress-stat">
                                <span class="stat-label">Avg Rating:</span>
                                <span class="stat-value">${data.avg_rating}</span>
                            </div>
                            <div class="progress-stat">
                                <span class="stat-label">Quizzes:</span>
                                <span class="stat-value">${data.quizzes}</span>
                            </div>
                            <div class="progress-stat">
                                <span class="stat-label">Passed:</span>
                                <span class="stat-value">${data.passed_quizzes}</span>
                            </div>
                            <div class="progress-stat">
                                <span class="stat-label">Avg Score:</span>
                                <span class="stat-value">${data.avg_score}%</span>
                            </div>
                        </div>
                    </div>
                `;
            });
            progressHTML += '</div>';
        }

        progressContainer.innerHTML = progressHTML;
    }

    async loadAchievements() {
        try {
            const token = localStorage.getItem('token');
            const response = await fetch('http://127.0.0.1:5000/api/dashboard/achievements', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                this.achievements = await response.json();
                this.displayAchievements();
            }
        } catch (error) {
            console.error('Error loading achievements:', error);
        }
    }

    displayAchievements() {
        if (!this.achievements) return;

        const achievementsContainer = document.getElementById('achievementsContainer');
        if (!achievementsContainer) return;

        let achievementsHTML = '<h3>Achievements</h3>';

        if (this.achievements.achievements.length === 0) {
            achievementsHTML += '<p>No achievements yet. Keep learning to earn badges!</p>';
        } else {
            achievementsHTML += '<div class="achievements-grid">';
            this.achievements.achievements.forEach(achievement => {
                achievementsHTML += `
                    <div class="achievement-card ${achievement.earned ? 'earned' : 'locked'}">
                        <div class="achievement-icon">${achievement.icon}</div>
                        <div class="achievement-content">
                            <h4>${achievement.title}</h4>
                            <p>${achievement.description}</p>
                        </div>
                    </div>
                `;
            });
            achievementsHTML += '</div>';
        }

        achievementsContainer.innerHTML = achievementsHTML;
    }

    async loadProfile() {
        try {
            const token = localStorage.getItem('token');
            const response = await fetch('http://127.0.0.1:5000/api/profile', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                this.displayProfile(data.profile);
            }
        } catch (error) {
            console.error('Error loading profile:', error);
        }
    }

    displayProfile(profile) {
        const profileContainer = document.getElementById('profileContainer');
        if (!profileContainer) return;

        profileContainer.innerHTML = `
            <div class="profile-info">
                <h3>Profile Information</h3>
                <div class="profile-details">
                    <p><strong>Name:</strong> ${profile.full_name}</p>
                    <p><strong>Email:</strong> ${profile.email}</p>
                    <p><strong>Grade Level:</strong> ${profile.grade_level || 'Not specified'}</p>
                    <p><strong>Subjects:</strong> ${profile.subjects.join(', ') || 'None selected'}</p>
                    <p><strong>Member since:</strong> ${new Date(profile.created_at).toLocaleDateString()}</p>
                    <p><strong>Email Verified:</strong> ${profile.email_verified ? 'Yes' : 'No'}</p>
                </div>
            </div>
        `;
    }

    async updateProfile() {
        try {
            const form = document.getElementById('profileForm');
            const formData = new FormData(form);
            
            const updateData = {
                full_name: formData.get('fullName'),
                grade_level: formData.get('gradeLevel'),
                subjects: formData.get('subjects').split(',').map(s => s.trim()).filter(s => s)
            };

            const token = localStorage.getItem('token');
            const response = await fetch('http://127.0.0.1:5000/api/profile', {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(updateData)
            });

            if (response.ok) {
                alert('Profile updated successfully!');
                this.loadProfile();
            } else {
                const error = await response.json();
                alert(`Error updating profile: ${error.error}`);
            }
        } catch (error) {
            console.error('Error updating profile:', error);
            alert('Error updating profile');
        }
    }

    async changePassword() {
        try {
            const form = document.getElementById('passwordForm');
            const formData = new FormData(form);
            
            const passwordData = {
                current_password: formData.get('currentPassword'),
                new_password: formData.get('newPassword')
            };

            const token = localStorage.getItem('token');
            const response = await fetch('http://127.0.0.1:5000/api/profile/change-password', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(passwordData)
            });

            if (response.ok) {
                alert('Password changed successfully!');
                form.reset();
            } else {
                const error = await response.json();
                alert(`Error changing password: ${error.error}`);
            }
        } catch (error) {
            console.error('Error changing password:', error);
            alert('Error changing password');
        }
    }

    showTab(tabName) {
        // Hide all tab contents
        document.querySelectorAll('.tab-content').forEach(tab => {
            tab.classList.remove('active');
        });

        // Remove active class from all tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });

        // Show selected tab content
        const selectedTab = document.getElementById(tabName + 'Tab');
        if (selectedTab) {
            selectedTab.classList.add('active');
        }

        // Add active class to clicked button
        event.target.classList.add('active');
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new Dashboard();
}); 
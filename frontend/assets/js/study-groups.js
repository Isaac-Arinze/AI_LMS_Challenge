// Study Groups JavaScript
class StudyGroups {
    constructor() {
        this.currentGroup = null;
        this.groups = [];
        this.messages = [];
        this.resources = [];
        this.init();
    }

    init() {
        this.loadGroups();
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Create group form
        const createGroupForm = document.getElementById('createGroupForm');
        if (createGroupForm) {
            createGroupForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.createGroup();
            });
        }

        // Join group buttons
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('join-group-btn')) {
                const groupId = e.target.dataset.groupId;
                this.joinGroup(groupId);
            }
            
            if (e.target.classList.contains('leave-group-btn')) {
                const groupId = e.target.dataset.groupId;
                this.leaveGroup(groupId);
            }
            
            if (e.target.classList.contains('view-group-btn')) {
                const groupId = e.target.dataset.groupId;
                this.viewGroup(groupId);
            }
        });

        // Message form
        const messageForm = document.getElementById('messageForm');
        if (messageForm) {
            messageForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.sendMessage();
            });
        }

        // Resource form
        const resourceForm = document.getElementById('resourceForm');
        if (resourceForm) {
            resourceForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.addResource();
            });
        }
    }

    async loadGroups() {
        try {
            const token = localStorage.getItem('token');
            if (!token) {
                console.error('No authentication token found');
                return;
            }

            const response = await fetch('http://127.0.0.1:5000/api/groups', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                this.groups = data.groups;
                this.displayGroups();
            } else {
                console.error('Failed to load groups');
            }
        } catch (error) {
            console.error('Error loading groups:', error);
        }
    }

    displayGroups() {
        const groupsContainer = document.getElementById('groupsContainer');
        if (!groupsContainer) return;

        if (this.groups.length === 0) {
            groupsContainer.innerHTML = `
                <div class="no-groups">
                    <h3>No Study Groups Available</h3>
                    <p>Be the first to create a study group!</p>
                </div>
            `;
            return;
        }

        const groupsHTML = this.groups.map(group => `
            <div class="group-card">
                <div class="group-header">
                    <h3>${group.name}</h3>
                    <span class="group-subject">${group.subject}</span>
                </div>
                <p class="group-description">${group.description}</p>
                <div class="group-meta">
                    <span class="group-topic">Topic: ${group.topic}</span>
                    <span class="group-members">${group.members.length}/${group.max_members} members</span>
                </div>
                <div class="group-actions">
                    <button class="btn btn-primary view-group-btn" data-group-id="${group._id}">
                        View Group
                    </button>
                    ${group.members.includes(localStorage.getItem('userId')) ? 
                        `<button class="btn btn-secondary leave-group-btn" data-group-id="${group._id}">Leave</button>` :
                        `<button class="btn btn-success join-group-btn" data-group-id="${group._id}">Join</button>`
                    }
                </div>
            </div>
        `).join('');

        groupsContainer.innerHTML = groupsHTML;
    }

    async createGroup() {
        try {
            const form = document.getElementById('createGroupForm');
            const formData = new FormData(form);
            
            const groupData = {
                name: formData.get('groupName'),
                description: formData.get('description'),
                subject: formData.get('subject'),
                topic: formData.get('topic'),
                max_members: parseInt(formData.get('maxMembers')),
                is_public: formData.get('isPublic') === 'true'
            };

            const token = localStorage.getItem('token');
            const response = await fetch('http://127.0.0.1:5000/api/groups', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(groupData)
            });

            if (response.ok) {
                const data = await response.json();
                alert('Group created successfully!');
                form.reset();
                this.loadGroups();
            } else {
                const error = await response.json();
                alert(`Error creating group: ${error.error}`);
            }
        } catch (error) {
            console.error('Error creating group:', error);
            alert('Error creating group');
        }
    }

    async joinGroup(groupId) {
        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`http://127.0.0.1:5000/api/groups/${groupId}/join`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                alert('Successfully joined group!');
                this.loadGroups();
            } else {
                const error = await response.json();
                alert(`Error joining group: ${error.error}`);
            }
        } catch (error) {
            console.error('Error joining group:', error);
            alert('Error joining group');
        }
    }

    async leaveGroup(groupId) {
        if (!confirm('Are you sure you want to leave this group?')) return;

        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`http://127.0.0.1:5000/api/groups/${groupId}/leave`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                alert('Successfully left group!');
                this.loadGroups();
            } else {
                const error = await response.json();
                alert(`Error leaving group: ${error.error}`);
            }
        } catch (error) {
            console.error('Error leaving group:', error);
            alert('Error leaving group');
        }
    }

    async viewGroup(groupId) {
        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`http://127.0.0.1:5000/api/groups/${groupId}`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                this.currentGroup = data.group;
                this.showGroupDetails();
                this.loadGroupMessages(groupId);
                this.loadGroupResources(groupId);
            } else {
                const error = await response.json();
                alert(`Error loading group: ${error.error}`);
            }
        } catch (error) {
            console.error('Error loading group:', error);
            alert('Error loading group');
        }
    }

    showGroupDetails() {
        const groupDetailsContainer = document.getElementById('groupDetailsContainer');
        if (!groupDetailsContainer || !this.currentGroup) return;

        const group = this.currentGroup;
        groupDetailsContainer.innerHTML = `
            <div class="group-details">
                <div class="group-header">
                    <h2>${group.name}</h2>
                    <button class="btn btn-secondary" onclick="studyGroups.hideGroupDetails()">Back to Groups</button>
                </div>
                <div class="group-info">
                    <p><strong>Subject:</strong> ${group.subject}</p>
                    <p><strong>Topic:</strong> ${group.topic}</p>
                    <p><strong>Description:</strong> ${group.description}</p>
                    <p><strong>Members:</strong> ${group.members.length}/${group.max_members}</p>
                </div>
                
                <div class="group-tabs">
                    <button class="tab-btn active" onclick="studyGroups.showTab('messages')">Messages</button>
                    <button class="tab-btn" onclick="studyGroups.showTab('resources')">Resources</button>
                    <button class="tab-btn" onclick="studyGroups.showTab('members')">Members</button>
                </div>
                
                <div id="messagesTab" class="tab-content active">
                    <div class="messages-container">
                        <div id="messagesList" class="messages-list"></div>
                        <form id="messageForm" class="message-form">
                            <input type="text" id="messageContent" placeholder="Type your message..." required>
                            <button type="submit" class="btn btn-primary">Send</button>
                        </form>
                    </div>
                </div>
                
                <div id="resourcesTab" class="tab-content">
                    <div class="resources-container">
                        <div id="resourcesList" class="resources-list"></div>
                        <form id="resourceForm" class="resource-form">
                            <input type="text" id="resourceTitle" placeholder="Resource title" required>
                            <input type="text" id="resourceUrl" placeholder="Resource URL (optional)">
                            <textarea id="resourceDescription" placeholder="Description (optional)"></textarea>
                            <button type="submit" class="btn btn-primary">Add Resource</button>
                        </form>
                    </div>
                </div>
                
                <div id="membersTab" class="tab-content">
                    <div id="membersList" class="members-list"></div>
                </div>
            </div>
        `;

        groupDetailsContainer.style.display = 'block';
        document.getElementById('groupsSection').style.display = 'none';
    }

    hideGroupDetails() {
        document.getElementById('groupDetailsContainer').style.display = 'none';
        document.getElementById('groupsSection').style.display = 'block';
        this.currentGroup = null;
    }

    showTab(tabName) {
        // Hide all tabs
        document.querySelectorAll('.tab-content').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });

        // Show selected tab
        document.getElementById(tabName + 'Tab').classList.add('active');
        event.target.classList.add('active');
    }

    async loadGroupMessages(groupId) {
        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`http://127.0.0.1:5000/api/groups/${groupId}/messages`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                this.messages = data.messages;
                this.displayMessages();
            }
        } catch (error) {
            console.error('Error loading messages:', error);
        }
    }

    displayMessages() {
        const messagesList = document.getElementById('messagesList');
        if (!messagesList) return;

        const messagesHTML = this.messages.map(message => `
            <div class="message">
                <div class="message-header">
                    <span class="message-author">${message.user_name}</span>
                    <span class="message-time">${new Date(message.created_at).toLocaleString()}</span>
                </div>
                <div class="message-content">${message.content}</div>
            </div>
        `).join('');

        messagesList.innerHTML = messagesHTML;
        messagesList.scrollTop = messagesList.scrollHeight;
    }

    async sendMessage() {
        try {
            const content = document.getElementById('messageContent').value;
            if (!content.trim()) return;

            const token = localStorage.getItem('token');
            const response = await fetch(`http://127.0.0.1:5000/api/groups/${this.currentGroup._id}/messages`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ content })
            });

            if (response.ok) {
                document.getElementById('messageContent').value = '';
                this.loadGroupMessages(this.currentGroup._id);
            } else {
                const error = await response.json();
                alert(`Error sending message: ${error.error}`);
            }
        } catch (error) {
            console.error('Error sending message:', error);
            alert('Error sending message');
        }
    }

    async loadGroupResources(groupId) {
        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`http://127.0.0.1:5000/api/groups/${groupId}/resources`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                this.resources = data.resources;
                this.displayResources();
            }
        } catch (error) {
            console.error('Error loading resources:', error);
        }
    }

    displayResources() {
        const resourcesList = document.getElementById('resourcesList');
        if (!resourcesList) return;

        if (this.resources.length === 0) {
            resourcesList.innerHTML = '<p>No resources shared yet.</p>';
            return;
        }

        const resourcesHTML = this.resources.map(resource => `
            <div class="resource-card">
                <h4>${resource.title}</h4>
                ${resource.description ? `<p>${resource.description}</p>` : ''}
                ${resource.url ? `<a href="${resource.url}" target="_blank" class="resource-link">View Resource</a>` : ''}
                <div class="resource-meta">
                    <span>Added: ${new Date(resource.created_at).toLocaleDateString()}</span>
                </div>
            </div>
        `).join('');

        resourcesList.innerHTML = resourcesHTML;
    }

    async addResource() {
        try {
            const title = document.getElementById('resourceTitle').value;
            const url = document.getElementById('resourceUrl').value;
            const description = document.getElementById('resourceDescription').value;

            if (!title.trim()) return;

            const token = localStorage.getItem('token');
            const response = await fetch(`http://127.0.0.1:5000/api/groups/${this.currentGroup._id}/resources`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ title, url, description })
            });

            if (response.ok) {
                document.getElementById('resourceForm').reset();
                this.loadGroupResources(this.currentGroup._id);
                alert('Resource added successfully!');
            } else {
                const error = await response.json();
                alert(`Error adding resource: ${error.error}`);
            }
        } catch (error) {
            console.error('Error adding resource:', error);
            alert('Error adding resource');
        }
    }
}

// Initialize study groups when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.studyGroups = new StudyGroups();
}); 
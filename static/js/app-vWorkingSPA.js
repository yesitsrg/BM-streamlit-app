/**
 * Beisman Maps Application JavaScript - Fixed Version
 */

class BeismanMapApp {
    constructor() {
        this.currentUser = null;
        this.currentPage = 'home';
        this.sessionId = null;
        this.pageHistory = ['home'];
        this.init();
    }

    async init() {
        console.log('🚀 Initializing Beisman Map Application...');
        await this.checkSession();
        this.setupEventListeners();
        this.updateAuthUI();
        this.loadCurrentPage();
        console.log('✅ Application initialized successfully');
    }

    setupEventListeners() {
        const adminLink = document.getElementById('admin-link');
        if (adminLink) {
            adminLink.addEventListener('click', (e) => {
                e.preventDefault();
                if (this.currentUser) {
                    this.logout();
                } else {
                    this.showLoginModal();
                }
            });
        }

        const loginForm = document.getElementById('login-form');
        if (loginForm) {
            loginForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleLogin();
            });
        }

        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal-backdrop')) {
                this.closeLoginModal();
            }
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeLoginModal();
            }
        });

        setInterval(() => {
            this.checkSession();
        }, 5 * 60 * 1000);
    }

    async checkSession() {
        try {
            const response = await fetch('/api/auth/session', {
                method: 'GET',
                credentials: 'include'
            });

            if (response.ok) {
                const sessionInfo = await response.json();
                if (sessionInfo.is_authenticated) {
                    this.currentUser = {
                        username: sessionInfo.username,
                        displayName: sessionInfo.display_name,
                        isAdmin: sessionInfo.is_admin,
                        sessionId: sessionInfo.session_id
                    };
                } else {
                    this.currentUser = null;
                }
            } else {
                this.currentUser = null;
            }
        } catch (error) {
            console.error('❌ Error checking session:', error);
            this.currentUser = null;
        }
        this.updateAuthUI();
    }

    updateAuthUI() {
        const adminLink = document.getElementById('admin-link');
        if (this.currentUser) {
            adminLink.textContent = 'Logout';
            adminLink.style.color = '#90EE90';
        } else {
            adminLink.textContent = 'Admin Login';
            adminLink.style.color = '#ffffff';
        }
    }

    showLoginModal() {
        const modal = document.getElementById('login-modal');
        if (modal) {
            modal.classList.remove('hidden');
            const usernameField = document.getElementById('username');
            if (usernameField) {
                setTimeout(() => usernameField.focus(), 100);
            }
        }
    }

    closeLoginModal() {
        const modal = document.getElementById('login-modal');
        if (modal) {
            modal.classList.add('hidden');
            const form = document.getElementById('login-form');
            if (form) {
                form.reset();
            }
            const errorDiv = document.getElementById('login-error');
            if (errorDiv) {
                errorDiv.classList.add('hidden');
                errorDiv.textContent = '';
            }
        }
    }

    async handleLogin() {
        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value.trim();

        if (!username || !password) {
            this.showLoginError('Please enter username and password');
            return;
        }

        try {
            const submitButton = document.querySelector('#login-form button[type="submit"]');
            const originalText = submitButton.textContent;
            submitButton.textContent = 'Logging in...';
            submitButton.disabled = true;

            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',
                body: JSON.stringify({
                    username: username,
                    password: password,
                    remember_me: false
                })
            });

            const result = await response.json();

            if (result.success) {
                this.currentUser = {
                    username: result.user_info.username,
                    displayName: result.user_info.display_name,
                    isAdmin: result.user_info.is_admin,
                    sessionId: result.session_id
                };
                this.closeLoginModal();
                this.updateAuthUI();
                this.navigateTo('admin-panel');
            } else {
                this.showLoginError(result.message || 'Login failed');
            }
        } catch (error) {
            console.error('❌ Login error:', error);
            this.showLoginError('Network error during login. Please try again.');
        } finally {
            const submitButton = document.querySelector('#login-form button[type="submit"]');
            submitButton.textContent = 'OK';
            submitButton.disabled = false;
        }
    }

    showLoginError(message) {
        const errorDiv = document.getElementById('login-error');
        if (errorDiv) {
            errorDiv.textContent = message;
            errorDiv.classList.remove('hidden');
        }
    }

    async logout() {
        try {
            const response = await fetch('/api/auth/logout', {
                method: 'POST',
                credentials: 'include'
            });

            const result = await response.json();
            
            if (result.success) {
                this.currentUser = null;
                this.updateAuthUI();
                this.hideAdminStatus(); // Hide admin status on logout
                this.navigateTo('home');
            }
        } catch (error) {
            console.error('❌ Logout error:', error);
        }
    }

    navigateTo(page, addToHistory = true) {
        console.log(`📍 Navigating to: ${page}`);
        
        if (addToHistory && page !== this.currentPage) {
            this.pageHistory.push(this.currentPage);
        }
        
        this.currentPage = page;
        this.updatePageTitle();
        this.loadCurrentPage();
    }

    goBack() {
        if (this.pageHistory.length > 0) {
            const previousPage = this.pageHistory.pop();
            this.navigateTo(previousPage, false);
        } else {
            this.navigateTo('home', false);
        }
    }

    updatePageTitle() {
        const pageTitle = document.getElementById('page-title');
        const pageTitles = {
            'home': 'Beisman Map Menu',
            'admin-panel': 'Beisman Map Menu - Admin Panel',
            'admin-login': 'Beisman Map Menu - Admin Login',
            'browse-maps': 'Browse Beisman Maps',
            'browse-entities': 'Browse Beisman Entities',
            'map-details': 'Map Information',
            'insert-map': 'Insert New Map',
            'update-delete': 'Update/Delete Map'
        };

        if (pageTitle) {
            pageTitle.textContent = pageTitles[this.currentPage] || 'Beisman Map Menu';
        }
    }

    loadCurrentPage() {
        const contentArea = document.getElementById('content-area');
        if (!contentArea) return;

        contentArea.innerHTML = '<div class="loading-content"><div class="loading-text">Loading...</div></div>';

        switch (this.currentPage) {
            case 'home':
                this.loadHomePage(contentArea);
                break;
            case 'admin-panel':
                this.loadAdminPanel(contentArea);
                break;
            case 'browse-maps':
                this.loadBrowseMaps(contentArea);
                break;
            case 'browse-entities':
                this.loadBrowseEntities(contentArea);
                break;
            case 'map-details':
                this.loadMapDetails(contentArea);
                break;
            case 'insert-map':
                this.loadInsertMap(contentArea);
                break;
            case 'update-delete':
                this.loadUpdateDelete(contentArea);
                break;
            default:
                this.loadHomePage(contentArea);
        }
    }

    loadHomePage(container) {
        container.innerHTML = `
            <div class="page-content">
                <div class="nav-container">
                    <a href="#" class="nav-link" onclick="beismanApp.navigateTo('browse-maps'); return false;">Browse Maps</a>
                    <a href="#" class="nav-link" onclick="beismanApp.navigateTo('browse-entities'); return false;">Browse Entities</a>
                </div>
            </div>
        `;
    }

    loadAdminPanel(container) {
        if (!this.currentUser?.isAdmin) {
            this.navigateTo('home');
            return;
        }

        container.innerHTML = `
            <div class="page-content">
                <div class="nav-container">
                    <a href="#" class="nav-link" onclick="beismanApp.navigateTo('browse-maps'); return false;">Browse Maps</a>
                    <a href="#" class="nav-link" onclick="beismanApp.navigateTo('browse-entities'); return false;">Browse Entities</a>
                    <a href="#" class="nav-link" onclick="beismanApp.navigateTo('insert-map'); return false;">Insert New Map</a>
                </div>
            </div>
        `;

        // Add admin status to body instead of content area
        this.showAdminStatus();
    }

    showAdminStatus() {
        // Remove any existing admin status
        const existing = document.querySelector('.admin-session-status');
        if (existing) {
            existing.remove();
        }

        // Create and append admin status directly to body
        const adminStatus = document.createElement('div');
        adminStatus.className = 'admin-session-status';
        adminStatus.textContent = 'Administrator Session Active';
        adminStatus.style.cssText = 'position: fixed !important; bottom: 5px !important; left: 20px !important; font-size: 10px !important; color: #000080 !important; font-style: italic !important; font-family: "MS Sans Serif", sans-serif !important; z-index: 9999 !important; pointer-events: none !important;';
        
        document.body.appendChild(adminStatus);
        console.log('✅ Admin status added to bottom of screen');
    }

    hideAdminStatus() {
        const existing = document.querySelector('.admin-session-status');
        if (existing) {
            existing.remove();
            console.log('✅ Admin status removed');
        }
    }

    async loadBrowseMaps(container) {
        try {
            let backDestination = this.currentUser?.isAdmin ? 'admin-panel' : 'home';
            let backText = this.currentUser?.isAdmin ? '← Back to Admin Panel' : '← Back to Main Menu';

            const response = await fetch('/api/maps?page=1&page_size=10', {
                credentials: 'include'
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();
            
            container.innerHTML = `
                <div class="page-content">
                    <a href="#" class="back-button" onclick="beismanApp.navigateTo('${backDestination}'); return false;">${backText}</a>
                    
                    <div class="search-container">
                        <div class="search-row">
                            <input type="text" id="maps-search" placeholder="Enter search term..." class="search-input">
                            <button onclick="beismanApp.searchMaps()" class="search-button">Search</button>
                            <button onclick="beismanApp.resetMapsSearch()" class="search-button">Reset</button>
                        </div>
                    </div>
                    
                    <div class="results-container">
                        ${this.renderMapsResults(data.data)}
                    </div>
                    
                    <div class="pagination">
                        <div class="pagination-info">
                            Page ${data.current_page} of ${data.total_pages}<br>
                            Displaying records 1 - ${data.data.length} of ${data.total_count}
                        </div>
                        ${this.renderPaginationButtons(data.current_page, data.total_pages, 'maps')}
                    </div>
                </div>
            `;
        } catch (error) {
            console.error('❌ Error loading maps:', error);
            container.innerHTML = `
                <div class="page-content">
                    <a href="#" class="back-button" onclick="beismanApp.goBack(); return false;">← Back</a>
                    <div class="status-message error">Failed to load maps data. Please check your connection and try again.</div>
                </div>
            `;
        }
    }

    async loadBrowseEntities(container) {
        try {
            let backDestination = this.currentUser?.isAdmin ? 'admin-panel' : 'home';
            let backText = this.currentUser?.isAdmin ? '← Back to Admin Panel' : '← Back to Main Menu';

            const response = await fetch('/api/entities?page=1&page_size=10', {
                credentials: 'include'
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();
            
            container.innerHTML = `
                <div class="page-content">
                    <a href="#" class="back-button" onclick="beismanApp.navigateTo('${backDestination}'); return false;">${backText}</a>
                    
                    <div class="alphabet-filter">
                        <div>Filter by first letter:</div>
                        <div class="alphabet-row">
                            ${'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('').map(letter => 
                                `<button class="alphabet-button" onclick="beismanApp.filterEntitiesByLetter('${letter}')">${letter}</button>`
                            ).join('')}
                            <button class="alphabet-button" onclick="beismanApp.filterEntitiesByLetter(null)">All</button>
                        </div>
                    </div>
                    
                    <div class="search-container">
                        <div class="search-row">
                            <input type="text" id="entities-search" placeholder="Enter search term..." class="search-input">
                            <button onclick="beismanApp.searchEntities()" class="search-button">Search</button>
                            <button onclick="beismanApp.resetEntitiesSearch()" class="search-button">Reset</button>
                        </div>
                    </div>
                    
                    <div class="results-container">
                        ${this.renderEntitiesResults(data.data)}
                    </div>
                    
                    <div class="pagination">
                        <div class="pagination-info">
                            Page ${data.current_page} of ${data.total_pages}<br>
                            Displaying records 1 - ${data.data.length} of ${data.total_count}
                        </div>
                        ${this.renderPaginationButtons(data.current_page, data.total_pages, 'entities')}
                    </div>
                </div>
            `;
        } catch (error) {
            console.error('❌ Error loading entities:', error);
            container.innerHTML = `
                <div class="page-content">
                    <a href="#" class="back-button" onclick="beismanApp.goBack(); return false;">← Back</a>
                    <div class="status-message error">Failed to load entities data. Please check your connection and try again.</div>
                </div>
            `;
        }
    }

    loadMapDetails(container) {
        const mapId = this.selectedMapId;
        const homeDestination = this.currentUser?.isAdmin ? 'admin-panel' : 'home';
        
        container.innerHTML = `
            <div class="page-content">
                <div id="map-details-content">Loading map details...</div>
                
                <div class="bottom-navigation">
                    <div class="nav-row">
                        <a href="#" class="nav-link" onclick="beismanApp.navigateTo('${homeDestination}'); return false;">Home</a>
                        <a href="#" class="nav-link" onclick="beismanApp.goBack(); return false;">Back</a>
                        <a href="#" class="nav-link" onclick="beismanApp.navigateTo('browse-maps'); return false;">Browse Maps</a>
                        <a href="#" class="nav-link" onclick="beismanApp.navigateTo('browse-entities'); return false;">Browse Entities</a>
                        ${this.currentUser?.isAdmin ? `
                            <a href="#" class="nav-link" onclick="beismanApp.navigateTo('insert-map'); return false;">Insert Map</a>
                            <a href="#" class="nav-link" onclick="beismanApp.navigateTo('update-delete'); return false;">Update/Delete</a>
                            <a href="#" class="nav-link" onclick="beismanApp.navigateTo('delete-entities'); return false;">Delete Entities</a>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;

        this.loadMapDetailsData(mapId);
    }

    async loadMapDetailsData(mapId) {
        try {
            const response = await fetch(`/api/maps/${mapId}`, {
                credentials: 'include'
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const mapData = await response.json();
            
            const detailsContent = document.getElementById('map-details-content');
            if (detailsContent) {
                detailsContent.innerHTML = `
                    <hr>
                    <div class="map-details">
                        <div class="detail-row">
                            <strong>Trace Number:</strong> ${mapData.Number || 'N/A'}
                        </div>
                        <div class="detail-row">
                            <strong>Drawer:</strong> ${mapData.Drawer || 'N/A'}
                        </div>
                        <div class="detail-row">
                            <strong>Description:</strong> ${mapData.PropertyDetails || 'N/A'}
                        </div>
                    </div>
                    <hr>
                    <div class="entities-section">
                        <strong>Associated Entities:</strong>
                        <div id="entities-list">Loading entities...</div>
                    </div>
                    <hr>
                `;
                
                this.loadMapEntities(mapId);
            }
        } catch (error) {
            console.error('❌ Error loading map details:', error);
            const detailsContent = document.getElementById('map-details-content');
            if (detailsContent) {
                detailsContent.innerHTML = '<div class="status-message error">Failed to load map details.</div>';
            }
        }
    }

    async loadMapEntities(mapId) {
        try {
            const response = await fetch(`/api/entities?search=${mapId}`, {
                credentials: 'include'
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const entitiesData = await response.json();
            
            const entitiesList = document.getElementById('entities-list');
            if (entitiesList) {
                if (entitiesData.data && entitiesData.data.length > 0) {
                    entitiesList.innerHTML = entitiesData.data.map(entity => 
                        `<div>${entity.EntityName}</div>`
                    ).join('');
                } else {
                    entitiesList.innerHTML = '<div class="status-message info">No clients associated with this map.</div>';
                }
            }
        } catch (error) {
            console.error('❌ Error loading map entities:', error);
            const entitiesList = document.getElementById('entities-list');
            if (entitiesList) {
                entitiesList.innerHTML = '<div class="status-message error">Failed to load entities.</div>';
            }
        }
    }

    loadInsertMap(container) {
        if (!this.currentUser?.isAdmin) {
            this.navigateTo('home');
            return;
        }

        container.innerHTML = `
            <div class="page-content">
                <a href="#" class="back-button" onclick="beismanApp.navigateTo('admin-panel'); return false;">← Back to Admin Panel</a>
                <hr>
                
                <div class="form-container">
                    <form id="insert-map-form">
                        <div class="form-group">
                            <label for="trace-number">Trace Number:</label>
                            <input type="text" id="trace-number" class="windows-input" required>
                        </div>
                        <div class="form-group">
                            <label for="drawer">Drawer:</label>
                            <input type="text" id="drawer" class="windows-input" required>
                        </div>
                        <div class="form-group">
                            <label for="description">Description:</label>
                            <textarea id="description" class="windows-input" rows="4" required></textarea>
                        </div>
                        <hr>
                        <div class="form-actions">
                            <button type="submit" class="windows-button primary">Insert</button>
                            <button type="button" class="windows-button" onclick="beismanApp.navigateTo('admin-panel')">Cancel</button>
                        </div>
                    </form>
                </div>
            </div>
        `;

        const form = document.getElementById('insert-map-form');
        if (form) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleInsertMap();
            });
        }
    }

    loadUpdateDelete(container) {
        if (!this.currentUser?.isAdmin) {
            this.navigateTo('home');
            return;
        }

        // Check if we have a selected map ID
        if (!this.selectedMapId) {
            container.innerHTML = `
                <div class="page-content">
                    <a href="#" class="back-button" onclick="beismanApp.navigateTo('admin-panel'); return false;">← Back to Admin Panel</a>
                    <div class="status-message warning">Please select a map first by clicking Details from Browse Maps.</div>
                </div>
            `;
            return;
        }

        // Show loading while we fetch the map data
        container.innerHTML = `
            <div class="page-content">
                <a href="#" class="back-button" onclick="beismanApp.navigateTo('map-details'); return false;">← Back to Map Details</a>
                <div class="loading-content"><div class="loading-text">Loading map for editing...</div></div>
            </div>
        `;

        // Load the map data for editing
        this.loadMapForEditing(container);
    }

    async loadMapForEditing(container) {
        try {
            console.log(`📝 Loading map ${this.selectedMapId} for editing`);

            // Fetch map data
            const mapResponse = await fetch(`/api/maps/${this.selectedMapId}`, {
                credentials: 'include'
            });

            if (!mapResponse.ok) {
                throw new Error(`Failed to load map: HTTP ${mapResponse.status}`);
            }

            const mapData = await mapResponse.json();
            console.log(`📋 Map data loaded:`, mapData);

            // Try to fetch entities for this map using the existing search method
            let mapEntities = [];
            try {
                const entitiesResponse = await fetch(`/api/entities?search=${this.selectedMapId}`, {
                    credentials: 'include'
                });

                if (entitiesResponse.ok) {
                    const entitiesResult = await entitiesResponse.json();
                    // Handle both possible response formats
                    if (entitiesResult.data && Array.isArray(entitiesResult.data)) {
                        mapEntities = entitiesResult.data;
                    } else if (Array.isArray(entitiesResult)) {
                        mapEntities = entitiesResult;
                    }
                    
                    // Filter entities that match this map number
                    mapEntities = mapEntities.filter(entity => 
                        entity.BeismanNumber == this.selectedMapId || 
                        entity.BeismanNumber === this.selectedMapId.toString()
                    );
                }
            } catch (entitiesError) {
                console.warn('Could not load entities:', entitiesError);
                mapEntities = [];
            }

            console.log(`👥 Found ${mapEntities.length} entities for this map`);

            // Render the edit form
            container.innerHTML = `
                <div class="page-content">
                    <a href="#" class="back-button" onclick="beismanApp.navigateTo('map-details'); return false;">← Back to Map Details</a>
                    
                    <div class="form-container">
                        <div class="form-header">Update Map Information</div>
                        
                        <form id="update-map-form">
                            <div class="form-group">
                                <label for="edit-trace-number">Trace Number:</label>
                                <input type="text" id="edit-trace-number" class="windows-input" value="${mapData.Number || ''}" readonly>
                                <small>Trace number cannot be changed</small>
                            </div>
                            
                            <div class="form-group">
                                <label for="edit-drawer">Drawer:</label>
                                <input type="text" id="edit-drawer" class="windows-input" value="${mapData.Drawer || ''}" required>
                            </div>
                            
                            <div class="form-group">
                                <label for="edit-description">Description:</label>
                                <textarea id="edit-description" class="windows-input" rows="4" required>${mapData.PropertyDetails || ''}</textarea>
                            </div>
                            
                            <div class="form-actions">
                                <button type="submit" class="windows-button primary">Update Map</button>
                                <button type="button" class="windows-button" onclick="beismanApp.navigateTo('map-details')">Cancel</button>
                            </div>
                        </form>
                    </div>

                    <hr>

                    <div class="entities-section">
                        <h3>Associated Entities</h3>
                        <div id="entities-edit-list">
                            ${this.renderEntitiesForEditing(mapEntities)}
                        </div>
                        
                        <div class="form-container" style="margin-top: 20px;">
                            <div class="form-header">Add New Entity</div>
                            <div class="form-row" style="display: flex; gap: 12px; align-items: end;">
                                <div class="form-group" style="flex: 1;">
                                    <label for="new-entity-name">Entity Name:</label>
                                    <input type="text" id="new-entity-name" class="windows-input" placeholder="Enter entity name">
                                </div>
                                <div class="form-group">
                                    <a href="#" class="nav-link" onclick="beismanApp.addEntityToMap(); return false;">Add</a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;

            // Add form submit handler for map update
            const form = document.getElementById('update-map-form');
            if (form) {
                form.addEventListener('submit', (e) => {
                    e.preventDefault();
                    this.handleUpdateMap();
                });
            }

        } catch (error) {
            console.error('❌ Error loading map for editing:', error);
            container.innerHTML = `
                <div class="page-content">
                    <a href="#" class="back-button" onclick="beismanApp.navigateTo('admin-panel'); return false;">← Back to Admin Panel</a>
                    <div class="status-message error">Failed to load map for editing: ${error.message}</div>
                </div>
            `;
        }
    }

    renderEntitiesForEditing(entities) {
        // Ensure entities is an array
        if (!entities || !Array.isArray(entities) || entities.length === 0) {
            return '<div class="status-message info">No entities associated with this map.</div>';
        }

        return entities.map(entity => `
            <div class="browse-row" style="display: flex; justify-content: space-between; align-items: center;">
                <div style="flex: 1;">${entity.EntityName || ''}</div>
                <div>
                    <a href="#" class="nav-link" onclick="beismanApp.removeEntityFromMap('${entity.EntityName}'); return false;" 
                       style="color: #ff0000;">Remove</a>
                </div>
            </div>
        `).join('');
    }

    async handleUpdateMap() {
        try {
            const drawer = document.getElementById('edit-drawer').value.trim();
            const description = document.getElementById('edit-description').value.trim();

            if (!drawer || !description) {
                alert('Please fill in both Drawer and Description fields.');
                return;
            }

            console.log(`💾 Updating map ${this.selectedMapId}`);

            // Show loading state
            const submitButton = document.querySelector('#update-map-form button[type="submit"]');
            const originalText = submitButton.textContent;
            submitButton.textContent = 'Updating...';
            submitButton.disabled = true;

            const response = await fetch(`/api/maps/${this.selectedMapId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',
                body: JSON.stringify({
                    Drawer: drawer,
                    PropertyDetails: description
                })
            });

            const result = await response.json();

            if (result.success) {
                alert('Map updated successfully!');
                console.log(`✅ Map ${this.selectedMapId} updated successfully`);
                // Refresh the editing view
                this.loadMapForEditing(document.getElementById('content-area'));
            } else {
                alert(result.message || 'Failed to update map');
            }

        } catch (error) {
            console.error('❌ Error updating map:', error);
            alert('Network error while updating map');
        } finally {
            // Reset button state
            const submitButton = document.querySelector('#update-map-form button[type="submit"]');
            if (submitButton) {
                submitButton.textContent = 'Update Map';
                submitButton.disabled = false;
            }
        }
    }

    async addEntityToMap() {
        try {
            const entityName = document.getElementById('new-entity-name').value.trim();

            if (!entityName) {
                alert('Please enter an entity name.');
                return;
            }

            console.log(`➕ Adding entity "${entityName}" to map ${this.selectedMapId}`);

            const response = await fetch(`/api/entities/map/${this.selectedMapId}/add?entity_name=${encodeURIComponent(entityName)}`, {
                method: 'POST',
                credentials: 'include'
            });

            const result = await response.json();

            if (result.success) {
                alert('Entity added successfully!');
                console.log(`✅ Entity "${entityName}" added to map ${this.selectedMapId}`);
                
                // Clear the input field
                document.getElementById('new-entity-name').value = '';
                
                // Refresh the editing view
                this.loadMapForEditing(document.getElementById('content-area'));
            } else {
                alert(result.message || 'Failed to add entity');
            }

        } catch (error) {
            console.error('❌ Error adding entity:', error);
            alert('Network error while adding entity');
        }
    }

    async removeEntityFromMap(entityName) {
        try {
            if (!confirm(`Are you sure you want to remove "${entityName}" from this map?`)) {
                return;
            }

            console.log(`🗑️ Removing entity "${entityName}" from map ${this.selectedMapId}`);

            const response = await fetch(`/api/entities/map/${this.selectedMapId}/${encodeURIComponent(entityName)}`, {
                method: 'DELETE',
                credentials: 'include'
            });

            const result = await response.json();

            if (result.success) {
                alert('Entity removed successfully!');
                console.log(`✅ Entity "${entityName}" removed from map ${this.selectedMapId}`);
                
                // Refresh the editing view
                this.loadMapForEditing(document.getElementById('content-area'));
            } else {
                alert(result.message || 'Failed to remove entity');
            }

        } catch (error) {
            console.error('❌ Error removing entity:', error);
            alert('Network error while removing entity');
        }
    }

    renderMapsResults(maps) {
        if (!maps || maps.length === 0) {
            return '<div class="status-message warning">No records found matching your search criteria.</div>';
        }

        return `
            <div class="browse-columns">
                <div class="column-header" style="flex: 1;">Details</div>
                <div class="column-header" style="flex: 2;">Number</div>
                <div class="column-header" style="flex: 2;">Drawer</div>
                <div class="column-header" style="flex: 4;">PropertyDetails</div>
            </div>
            ${maps.map(map => `
                <div class="browse-row">
                    <div style="flex: 1;">
                        <a href="#" class="nav-link" onclick="beismanApp.showMapDetails('${map.Number}'); return false;">Details</a>
                    </div>
                    <div style="flex: 2;">${map.Number || ''}</div>
                    <div style="flex: 2;">${map.Drawer || ''}</div>
                    <div style="flex: 4;">${map.PropertyDetails || ''}</div>
                </div>
            `).join('')}
        `;
    }

    renderEntitiesResults(entities) {
        if (!entities || entities.length === 0) {
            return '<div class="status-message warning">No records found matching your search criteria.</div>';
        }

        return `
            <div class="browse-columns">
                <div class="column-header" style="flex: 1;">Details</div>
                <div class="column-header" style="flex: 4;">Entity Name</div>
                <div class="column-header" style="flex: 2;">Map Number</div>
            </div>
            ${entities.map(entity => `
                <div class="browse-row">
                    <div style="flex: 1;">
                        <a href="#" class="nav-link" onclick="beismanApp.showMapDetails(${entity.BeismanNumber}); return false;">Details</a>
                    </div>
                    <div style="flex: 4;">${entity.EntityName || ''}</div>
                    <div style="flex: 2;">${entity.BeismanNumber || ''}</div>
                </div>
            `).join('')}
        `;
    }

    renderPaginationButtons(currentPage, totalPages, type) {
        if (totalPages <= 1) return '';

        let buttons = '';
        
        if (currentPage > 1) {
            buttons += `<button class="pagination-button" onclick="beismanApp.loadPage('${type}', ${currentPage - 1})">⬅️ Previous</button>`;
        }
        
        if (currentPage < totalPages) {
            buttons += `<button class="pagination-button" onclick="beismanApp.loadPage('${type}', ${currentPage + 1})">Next ➡️</button>`;
        }
        
        return buttons;
    }

    showMapDetails(mapId) {
        this.selectedMapId = mapId;
        this.navigateTo('map-details');
    }

    async handleInsertMap() {
        const traceNumber = document.getElementById('trace-number').value.trim();
        const drawer = document.getElementById('drawer').value.trim();
        const description = document.getElementById('description').value.trim();

        if (!traceNumber || !drawer || !description) {
            alert('Please fill in all fields.');
            return;
        }

        try {
            const response = await fetch('/api/maps', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',
                body: JSON.stringify({
                    Number: traceNumber,
                    Drawer: drawer,
                    PropertyDetails: description,
                    CreatedBy: this.currentUser.username
                })
            });

            const result = await response.json();

            if (result.success) {
                alert('Map inserted successfully!');
                document.getElementById('insert-map-form').reset();
            } else {
                alert(result.message || 'Failed to insert map');
            }
        } catch (error) {
            console.error('❌ Error inserting map:', error);
            alert('Network error while inserting map');
        }
    }

    async searchMaps() {
        try {
            const searchTerm = document.getElementById('maps-search').value.trim();
            console.log(`🔍 Searching maps for: "${searchTerm}"`);

            // Show loading state
            const resultsContainer = document.querySelector('.results-container');
            if (resultsContainer) {
                resultsContainer.innerHTML = '<div class="loading-content"><div class="loading-text">Searching...</div></div>';
            }

            // Build API URL with search term
            let apiUrl = '/api/maps?page=1&page_size=50';
            if (searchTerm) {
                apiUrl += `&search=${encodeURIComponent(searchTerm)}`;
            }

            console.log(`📡 Making API call to: ${apiUrl}`);

            // Make API call
            const response = await fetch(apiUrl, {
                credentials: 'include'
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();
            console.log(`📊 Search returned ${data.data.length} maps`);

            // Update the results display
            if (resultsContainer) {
                resultsContainer.innerHTML = this.renderMapsResults(data.data);
            }

            // Update pagination info to show search results
            const paginationDiv = document.querySelector('.pagination');
            if (paginationDiv) {
                const paginationInfo = paginationDiv.querySelector('.pagination-info');
                if (paginationInfo) {
                    if (searchTerm) {
                        paginationInfo.innerHTML = `
                            Search results for "${searchTerm}"<br>
                            ${data.data.length} record(s) found
                        `;
                    } else {
                        paginationInfo.innerHTML = `
                            Page ${data.current_page} of ${data.total_pages}<br>
                            Displaying records 1 - ${data.data.length} of ${data.total_count}
                        `;
                    }
                }

                // Hide pagination buttons when searching
                const paginationButtons = paginationDiv.querySelectorAll('.pagination-button');
                paginationButtons.forEach(button => {
                    button.style.display = searchTerm ? 'none' : 'inline-block';
                });
            }

            console.log(`🎉 Maps search completed successfully`);

        } catch (error) {
            console.error('❌ Error searching maps:', error);
            const resultsContainer = document.querySelector('.results-container');
            if (resultsContainer) {
                resultsContainer.innerHTML = '<div class="status-message error">Failed to search maps. Please try again.</div>';
            }
        }
    }

    resetMapsSearch() {
        document.getElementById('maps-search').value = '';
        this.loadCurrentPage();
    }

    async searchEntities() {
        try {
            const searchTerm = document.getElementById('entities-search').value.trim();
            console.log(`🔍 Searching entities for: "${searchTerm}"`);

            // Show loading state
            const resultsContainer = document.querySelector('.results-container');
            if (resultsContainer) {
                resultsContainer.innerHTML = '<div class="loading-content"><div class="loading-text">Searching...</div></div>';
            }

            // Build API URL with search term
            let apiUrl = '/api/entities?page=1&page_size=50';
            if (searchTerm) {
                apiUrl += `&search=${encodeURIComponent(searchTerm)}`;
            }

            console.log(`📡 Making API call to: ${apiUrl}`);

            // Make API call
            const response = await fetch(apiUrl, {
                credentials: 'include'
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();
            console.log(`📊 Search returned ${data.data.length} entities`);

            // Update the results display
            if (resultsContainer) {
                resultsContainer.innerHTML = this.renderEntitiesResults(data.data);
            }

            // Update pagination info to show search results
            const paginationDiv = document.querySelector('.pagination');
            if (paginationDiv) {
                const paginationInfo = paginationDiv.querySelector('.pagination-info');
                if (paginationInfo) {
                    if (searchTerm) {
                        paginationInfo.innerHTML = `
                            Search results for "${searchTerm}"<br>
                            ${data.data.length} record(s) found
                        `;
                    } else {
                        paginationInfo.innerHTML = `
                            Page ${data.current_page} of ${data.total_pages}<br>
                            Displaying records 1 - ${data.data.length} of ${data.total_count}
                        `;
                    }
                }

                // Hide pagination buttons when searching
                const paginationButtons = paginationDiv.querySelectorAll('.pagination-button');
                paginationButtons.forEach(button => {
                    button.style.display = searchTerm ? 'none' : 'inline-block';
                });
            }

            console.log(`🎉 Entities search completed successfully`);

        } catch (error) {
            console.error('❌ Error searching entities:', error);
            const resultsContainer = document.querySelector('.results-container');
            if (resultsContainer) {
                resultsContainer.innerHTML = '<div class="status-message error">Failed to search entities. Please try again.</div>';
            }
        }
    }

    resetEntitiesSearch() {
        document.getElementById('entities-search').value = '';
        this.loadCurrentPage();
    }

    async filterEntitiesByLetter(letter) {
        try {
            console.log(`🔍 Starting filter for letter: ${letter}`);
            
            // Show loading state
            const resultsContainer = document.querySelector('.results-container');
            if (resultsContainer) {
                resultsContainer.innerHTML = '<div class="loading-content"><div class="loading-text">Filtering...</div></div>';
            }

            // Get current search term if any
            let searchTerm = '';
            const searchInput = document.getElementById('entities-search');
            if (searchInput) {
                searchTerm = searchInput.value.trim();
            }

            // Build API URL - get more entities to filter from
            let apiUrl = '/api/entities?page=1&page_size=100';
            
            if (searchTerm) {
                apiUrl += `&search=${encodeURIComponent(searchTerm)}`;
            }

            console.log(`📡 Making API call to: ${apiUrl}`);

            // Make API call
            const response = await fetch(apiUrl, {
                credentials: 'include'
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();
            console.log(`📊 Received ${data.data.length} entities from API`);

            let filteredEntities = data.data;

            // Apply letter filtering if a letter was selected
            if (letter) {
                filteredEntities = data.data.filter(entity => {
                    const entityName = entity.EntityName || '';
                    const startsWithLetter = entityName.toLowerCase().startsWith(letter.toLowerCase());
                    return startsWithLetter;
                });
                
                console.log(`✅ After filtering by '${letter}': ${filteredEntities.length} entities found`);
            } else {
                console.log(`✅ Showing all entities: ${filteredEntities.length} entities`);
            }

            // Update the results display
            if (resultsContainer) {
                resultsContainer.innerHTML = this.renderEntitiesResults(filteredEntities);
            }

            // Update pagination info to show filter status
            const paginationDiv = document.querySelector('.pagination');
            if (paginationDiv) {
                const paginationInfo = paginationDiv.querySelector('.pagination-info');
                if (paginationInfo) {
                    if (letter) {
                        paginationInfo.innerHTML = `
                            Showing entities starting with '${letter}'<br>
                            ${filteredEntities.length} record(s) found
                        `;
                    } else {
                        paginationInfo.innerHTML = `
                            Showing all entities<br>
                            ${filteredEntities.length} record(s) found
                        `;
                    }
                }
                
                // Hide pagination buttons when filtering
                const paginationButtons = paginationDiv.querySelectorAll('.pagination-button');
                paginationButtons.forEach(button => {
                    button.style.display = letter ? 'none' : 'inline-block';
                });
            }

            console.log(`🎉 Filtering completed successfully`);

        } catch (error) {
            console.error('❌ Error filtering entities:', error);
            const resultsContainer = document.querySelector('.results-container');
            if (resultsContainer) {
                resultsContainer.innerHTML = '<div class="status-message error">Failed to filter entities. Please try again.</div>';
            }
        }
    }

    async loadPage(type, page) {
        console.log('Loading page:', type, page);
    }
}

function navigateTo(page) {
    if (window.beismanApp) {
        window.beismanApp.navigateTo(page);
    }
}

function closeLoginModal() {
    if (window.beismanApp) {
        window.beismanApp.closeLoginModal();
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.beismanApp = new BeismanMapApp();
});

console.log('📄 Beisman Map Application script loaded successfully');
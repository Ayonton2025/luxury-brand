// Admin Dashboard Functionality
document.addEventListener('DOMContentLoaded', function() {
    // Initialize admin functionality
    initTabs();
    loadDashboardData();
    loadProducts();
    loadSections();
    initProductModal();

    // Load additional tabs by default inactive but ready
    // These can also be loaded lazily on tab click if preferred
    loadMessages();
    loadSubscribers();
    loadVideos();
    loadGiveaway();
});


// Tab functionality
function initTabs() {
    const menuItems = document.querySelectorAll('.menu-item');
    const tabContents = document.querySelectorAll('.tab-content');
    
    menuItems.forEach(item => {
        if (item.dataset.tab) {
            item.addEventListener('click', function() {
                const tabId = this.dataset.tab;

                // Update the tab title header
                const titleMap = {
                    dashboard: 'Dashboard',
                    products: 'Products',
                    testimonials: 'Testimonials',
                    videos: 'Videos',
                    giveaway: 'Giveaway',
                    messages: 'Messages',
                    subscribers: 'Subscribers',
                    sections: 'Section Visibility',
                };
                document.getElementById('tab-title').textContent = titleMap[tabId] || '';

                // Remove active class from all menu items and tabs
                menuItems.forEach(i => i.classList.remove('active'));
                tabContents.forEach(t => t.classList.remove('active'));
                
                // Add active class to clicked menu item and corresponding tab
                this.classList.add('active');
                document.getElementById(`${tabId}-tab`).classList.add('active');
                
                // Load data for the selected tab
                switch(tabId){
                    case 'products': loadProducts(); break;
                    case 'sections': loadSections(); break;
                    case 'messages': loadMessages(); break;
                    case 'subscribers': loadSubscribers(); break;
                    case 'videos': loadVideos(); break;
                    case 'giveaway': loadGiveaway(); break;
                    // Add others as needed
                }
            });
        }
    });
}


// Load dashboard data
function loadDashboardData() {
    // Fetch various admin stats
    fetch('/api/admin/stats')
        .then(response => response.json())
        .then(stats => {
            document.getElementById('views-count').textContent = stats.page_views || 0;
            document.getElementById('orders-count').textContent = stats.orders || 0;
            document.getElementById('users-count').textContent = stats.users || 0;
            document.getElementById('subscribers-count').textContent = stats.subscribers || 0;
            document.getElementById('messages-count').textContent = stats.unread_messages || 0;
        });

    // Load recent messages snippet for dashboard
    fetch('/api/admin/messages?limit=5')
        .then(response => response.json())
        .then(messages => {
            const recentMessages = document.getElementById('recent-messages');
            recentMessages.innerHTML = '';
            messages.forEach(message => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${message.name}</td>
                    <td>${message.email}</td>
                    <td>${message.message.substring(0, 50)}${message.message.length > 50 ? '...' : ''}</td>
                    <td>${new Date(message.created_at).toLocaleDateString()}</td>
                    <td><button class="btn-secondary view-message" data-id="${message.id}">View</button></td>
                `;
                recentMessages.appendChild(tr);
            });
            initMessageViewButtons();
        });
}


// Load products
function loadProducts() {
    fetch('/api/admin/products')
        .then(response => response.json())
        .then(products => {
            const productsTable = document.getElementById('products-table');
            productsTable.innerHTML = '';
            
            products.forEach(product => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><img src="${product.image ? '/uploads/products/' + product.image : 'https://via.placeholder.com/50x50'}" alt="${product.name}"></td>
                    <td>${product.name}</td>
                    <td>${product.description.substring(0, 50)}${product.description.length > 50 ? '...' : ''}</td>
                    <td>$${product.price.toFixed(2)}</td>
                    <td>${product.visible ? 'Visible' : 'Hidden'}</td>
                    <td>
                        <button class="btn-secondary edit-product" data-id="${product.id}">Edit</button>
                        <button class="btn-danger delete-product" data-id="${product.id}">Delete</button>
                    </td>
                `;
                productsTable.appendChild(tr);
            });
            
            // Add event listeners to edit and delete buttons
            document.querySelectorAll('.edit-product').forEach(btn => {
                btn.addEventListener('click', function() {
                    const productId = this.dataset.id;
                    editProduct(productId);
                });
            });
            
            document.querySelectorAll('.delete-product').forEach(btn => {
                btn.addEventListener('click', function() {
                    const productId = this.dataset.id;
                    deleteProduct(productId);
                });
            });
        });
}


// Load section visibility settings
function loadSections() {
    fetch('/api/admin/sections')
        .then(response => response.json())
        .then(sections => {
            const sectionContainer = document.getElementById('section-visibility');
            sectionContainer.innerHTML = '';
            
            sections.forEach(section => {
                const div = document.createElement('div');
                div.className = 'toggle-card';
                div.innerHTML = `
                    <div class="toggle-info">
                        <h3>${capitalize(section.section_name)} Section</h3>
                        <p>Show or hide the ${section.section_name} section on the main website</p>
                    </div>
                    <label class="toggle-switch">
                        <input type="checkbox" data-section="${section.section_name}" ${section.visible ? 'checked' : ''}>
                        <span class="slider"></span>
                    </label>
                `;
                sectionContainer.appendChild(div);
            });
        });
}

// Utility function for capitalization
function capitalize(s) {
    if (typeof s !== 'string') return '';
    return s.charAt(0).toUpperCase() + s.slice(1);
}


// Initialize product modal (same as given)
function initProductModal() {
    const modal = document.getElementById('product-modal');
    const addProductBtn = document.getElementById('add-product-btn');
    const closeModal = document.querySelector('.close-modal');
    const productForm = document.getElementById('product-form');
    
    // Open modal for adding new product
    addProductBtn.addEventListener('click', function() {
        document.getElementById('product-modal-title').textContent = 'Add New Product';
        productForm.reset();
        document.getElementById('product-id').value = '';
        document.getElementById('image-preview').innerHTML = '';
        modal.classList.add('active');
    });
    
    // Close modal
    closeModal.addEventListener('click', function() {
        modal.classList.remove('active');
    });
    
    // Close modal when clicking outside
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            modal.classList.remove('active');
        }
    });
    
    // Handle image preview
    document.getElementById('product-image').addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                document.getElementById('image-preview').innerHTML = `<img src="${e.target.result}" alt="Preview">`;
            };
            reader.readAsDataURL(file);
        }
    });
    
    // Handle form submission (POST/PUT)
    productForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData();
        formData.append('name', document.getElementById('product-name').value);
        formData.append('description', document.getElementById('product-description').value);
        formData.append('details', document.getElementById('product-details').value);
        formData.append('price', document.getElementById('product-price').value);
        formData.append('visible', document.getElementById('product-visible').checked);
        
        const productId = document.getElementById('product-id').value;
        if (productId) formData.append('id', productId);
        
        const imageFile = document.getElementById('product-image').files[0];
        if (imageFile) formData.append('image', imageFile);
        
        const url = productId ? '/api/admin/products' : '/api/admin/products';
        const method = productId ? 'PUT' : 'POST';
        
        fetch(url, { method, body: formData })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            if (data.success) {
                modal.classList.remove('active');
                loadProducts();
            }
        })
        .catch(() => alert('An error occurred. Please try again.'));
    });
}

// Edit and delete products - same as given
// ...


/* New additions for messages, subscribers, videos, giveaway */

// Load messages
function loadMessages(){
    fetch('/api/admin/messages')
    .then(res => res.json())
    .then(messages => {
        const table = document.getElementById('messages-table');
        table.innerHTML = '';
        messages.forEach(m => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${m.name}</td>
                <td>${m.email}</td>
                <td>${m.message}</td>
                <td>${new Date(m.created_at).toLocaleString()}</td>
                <td><button class="btn-secondary view-message" data-id="${m.id}">View</button></td>
            `;
            table.appendChild(tr);
        });
        initMessageViewButtons();
    });
}
// Initialize message view buttons to show details or mark read (this is a placeholder)
function initMessageViewButtons(){
    document.querySelectorAll('.view-message').forEach(btn => {
        btn.onclick = () => alert('Message detail modal or page can be implemented here (Message ID: '+btn.dataset.id+')');
    });
}

// Load subscribers
function loadSubscribers(){
    fetch('/api/admin/subscribers')
    .then(res => res.json())
    .then(subs => {
        const table = document.getElementById('subscribers-table');
        table.innerHTML = '';
        subs.forEach(s => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${s.email}</td>
                <td>${new Date(s.created_at).toLocaleDateString()}</td>
                <td><button class="btn-danger delete-subscriber" data-id="${s.id}">Delete</button></td>
            `;
            table.appendChild(tr);
        });
        initSubscriberDeleteButtons();
    });
}
function initSubscriberDeleteButtons(){
    document.querySelectorAll('.delete-subscriber').forEach(btn => {
        btn.onclick = () => {
            if(confirm('Delete this subscriber?')){
                fetch('/api/admin/subscribers', {
                    method: 'DELETE',
                    headers: {'Content-Type':'application/json'},
                    body: JSON.stringify({id: btn.dataset.id})
                }).then(res => res.json())
                .then(data => {
                    alert(data.message);
                    if(data.success) loadSubscribers();
                }).catch(() => alert('Failed to delete subscriber.'));
            }
        };
    });
}

// Load videos
function loadVideos(){
    fetch('/api/admin/videos')
    .then(res => res.json())
    .then(videos => {
        const table = document.getElementById('videos-table');
        table.innerHTML = '';
        videos.forEach(v => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${v.title}</td>
                <td>${v.description}</td>
                <td>${v.video_url}</td>
                <td><img src="${v.thumbnail_url || 'https://via.placeholder.com/100x60'}" alt="Thumbnail" style="width:100px;"></td>
                <td>
                    <button class="btn-secondary edit-video" data-id="${v.id}">Edit</button>
                    <button class="btn-danger delete-video" data-id="${v.id}">Delete</button>
                </td>
            `;
            table.appendChild(tr);
        });
        initVideoButtons();
    });
}

function initVideoButtons(){
    document.querySelectorAll('.edit-video').forEach(btn => {
        btn.onclick = () => alert('Edit video modal/page placeholder (ID: '+btn.dataset.id+')');
    });
    document.querySelectorAll('.delete-video').forEach(btn => {
        btn.onclick = () => {
            if(confirm('Delete this video?')){
                fetch('/api/admin/videos', {
                    method: 'DELETE',
                    headers: {'Content-Type':'application/json'},
                    body: JSON.stringify({id: btn.dataset.id})
                })
                .then(res => res.json())
                .then(data => {
                    alert(data.message);
                    if(data.success) loadVideos();
                }).catch(() => alert('Failed to delete video.'));
            }
        };
    });
}

// Load giveaway info
function loadGiveaway(){
    fetch('/api/admin/giveaway')
    .then(res => res.json())
    .then(giveaway => {
        const table = document.getElementById('giveaway-table');
        table.innerHTML = '';
        if(giveaway) {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${giveaway.title}</td>
                <td>${giveaway.description}</td>
                <td><img src="${giveaway.image_url || 'https://via.placeholder.com/100x60'}" alt="Giveaway Image" style="width:100px;"></td>
                <td>${new Date(giveaway.end_date).toLocaleDateString()}</td>
                <td>${giveaway.participants_count}</td>
                <td>
                    <button class="btn-secondary edit-giveaway" data-id="${giveaway.id}">Edit</button>
                    <button class="btn-danger delete-giveaway" data-id="${giveaway.id}">Delete</button>
                </td>
            `;
            table.appendChild(tr);
            initGiveawayButtons();
        } else {
            table.innerHTML = '<tr><td colspan="6">No current giveaway set.</td></tr>';
        }
    });
}

function initGiveawayButtons(){
    document.querySelectorAll('.edit-giveaway').forEach(btn => {
        btn.onclick = () => alert('Edit giveaway modal/page placeholder (ID: '+btn.dataset.id+')');
    });
    document.querySelectorAll('.delete-giveaway').forEach(btn => {
        btn.onclick = () => {
            if(confirm('Delete this giveaway?')){
                fetch('/api/admin/giveaway', {
                    method: 'DELETE',
                    headers: {'Content-Type':'application/json'},
                    body: JSON.stringify({id: btn.dataset.id})
                })
                .then(res => res.json())
                .then(data => {
                    alert(data.message);
                    if(data.success) loadGiveaway();
                }).catch(() => alert('Failed to delete giveaway.'));
            }
        };
    });
}

// Save section visibility
document.getElementById('save-sections-btn').addEventListener('click', function() {
    const sections = [];
    document.querySelectorAll('#section-visibility input[type="checkbox"]').forEach(checkbox => {
        sections.push({
            section_name: checkbox.dataset.section,
            visible: checkbox.checked
        });
    });
    
    fetch('/api/admin/sections', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(sections)
    })
    .then(response => response.json())
    .then(data => alert(data.message))
    .catch(() => alert('An error occurred. Please try again.'));
});

// User profile dropdown toggle
document.addEventListener('DOMContentLoaded', function() {
    const userProfile = document.querySelector('.user-profile');
    if (!userProfile) return;

    userProfile.addEventListener('click', function(e) {
        e.stopPropagation();
        this.classList.toggle('active');
    });

    // Close dropdown when clicking outside
    document.addEventListener('click', function() {
        if (userProfile.classList.contains('active')) {
            userProfile.classList.remove('active');
        }
    });
});

// Utility function to capitalize
function capitalize(s) {
    if(typeof s !== 'string') return '';
    return s.charAt(0).toUpperCase() + s.slice(1);
}

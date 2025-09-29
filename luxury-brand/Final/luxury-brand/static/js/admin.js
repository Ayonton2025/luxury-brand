// Admin Dashboard Functionality
document.addEventListener('DOMContentLoaded', function() {
    // Initialize admin functionality
    initTabs();
    loadDashboardData();
    loadProducts();
    loadSections();
    initProductModal();
});

// Tab functionality
function initTabs() {
    const menuItems = document.querySelectorAll('.menu-item');
    const tabContents = document.querySelectorAll('.tab-content');
    
    menuItems.forEach(item => {
        if (item.dataset.tab) {
            item.addEventListener('click', function() {
                const tabId = this.dataset.tab;
                
                // Remove active class from all menu items and tabs
                menuItems.forEach(i => i.classList.remove('active'));
                tabContents.forEach(t => t.classList.remove('active'));
                
                // Add active class to clicked menu item and corresponding tab
                this.classList.add('active');
                document.getElementById(`${tabId}-tab`).classList.add('active');
                
                // Load data for the selected tab
                if (tabId === 'products') {
                    loadProducts();
                } else if (tabId === 'sections') {
                    loadSections();
                } else if (tabId === 'messages') {
                    loadMessages();
                } else if (tabId === 'subscribers') {
                    loadSubscribers();
                }
            });
        }
    });
}

// Load dashboard data
function loadDashboardData() {
    // Load stats
    fetch('/api/admin/subscribers')
        .then(response => response.json())
        .then(subscribers => {
            document.getElementById('subscribers-count').textContent = subscribers.length;
        });
    
    fetch('/api/admin/messages')
        .then(response => response.json())
        .then(messages => {
            document.getElementById('messages-count').textContent = messages.filter(m => !m.read).length;
            
            // Load recent messages
            const recentMessages = document.getElementById('recent-messages');
            recentMessages.innerHTML = '';
            
            messages.slice(0, 5).forEach(message => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${message.name}</td>
                    <td>${message.email}</td>
                    <td>${message.message.substring(0, 50)}${message.message.length > 50 ? '...' : ''}</td>
                    <td>${new Date(message.created_at).toLocaleDateString()}</td>
                    <td>
                        <button class="btn-secondary" data-id="${message.id}">View</button>
                    </td>
                `;
                recentMessages.appendChild(tr);
            });
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
                        <h3>${section.section_name.charAt(0).toUpperCase() + section.section_name.slice(1)} Section</h3>
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

// Initialize product modal
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
    
    // Handle form submission
    productForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData();
        formData.append('name', document.getElementById('product-name').value);
        formData.append('description', document.getElementById('product-description').value);
        formData.append('details', document.getElementById('product-details').value);
        formData.append('price', document.getElementById('product-price').value);
        formData.append('visible', document.getElementById('product-visible').checked);
        
        const productId = document.getElementById('product-id').value;
        if (productId) {
            formData.append('id', productId);
        }
        
        const imageFile = document.getElementById('product-image').files[0];
        if (imageFile) {
            formData.append('image', imageFile);
        }
        
        const url = productId ? '/api/admin/products' : '/api/admin/products';
        const method = productId ? 'PUT' : 'POST';
        
        fetch(url, {
            method: method,
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            if (data.success) {
                modal.classList.remove('active');
                loadProducts();
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred. Please try again.');
        });
    });
}

// Edit product
function editProduct(productId) {
    fetch('/api/admin/products')
        .then(response => response.json())
        .then(products => {
            const product = products.find(p => p.id == productId);
            if (product) {
                document.getElementById('product-modal-title').textContent = 'Edit Product';
                document.getElementById('product-id').value = product.id;
                document.getElementById('product-name').value = product.name;
                document.getElementById('product-description').value = product.description;
                document.getElementById('product-details').value = product.details;
                document.getElementById('product-price').value = product.price;
                document.getElementById('product-visible').checked = product.visible;
                
                // Show image preview if exists
                const imagePreview = document.getElementById('image-preview');
                imagePreview.innerHTML = '';
                if (product.image) {
                    imagePreview.innerHTML = `<img src="/uploads/products/${product.image}" alt="Preview">`;
                }
                
                // Show modal
                document.getElementById('product-modal').classList.add('active');
            }
        });
}

// Delete product
function deleteProduct(productId) {
    if (confirm('Are you sure you want to delete this product?')) {
        fetch('/api/admin/products', {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ id: productId })
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            if (data.success) {
                loadProducts();
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred. Please try again.');
        });
    }
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
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(sections)
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
    });
});

// Additional functions for messages, subscribers, etc. would be implemented here
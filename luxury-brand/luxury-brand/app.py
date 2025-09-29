from flask import Flask, render_template, request, jsonify, send_from_directory, session, redirect, url_for, flash
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from PIL import Image
from datetime import datetime
from flask import abort

# Import config and database models
from config import Config
from database import (
    db, Product, Testimonial, Video, Giveaway, Subscriber, Message,
    SectionVisibility, User, Order, Notification, CartItem, WishlistItem, init_db
)

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Ensure upload folder and subfolders exist
base_upload = app.config.get('UPLOAD_FOLDER', 'static/uploads')
os.makedirs(base_upload, exist_ok=True)
for sub in ['products', 'giveaway', 'videos']:
    os.makedirs(os.path.join(base_upload, sub), exist_ok=True)

# Initialize SQLAlchemy app
db.init_app(app)

# Initialize database with default sections and admin user
with app.app_context():
    init_db()

# -------------------------
# Helper functions
# -------------------------
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def save_image(file, folder, max_size=(800, 800)):
    """
    Save an uploaded image safely and resize it.
    Returns filename or None.
    """
    if not file or not file.filename or not allowed_file(file.filename):
        return None

    filename = secure_filename(file.filename)
    filename = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{filename}"
    folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder)
    os.makedirs(folder_path, exist_ok=True)
    filepath = os.path.join(folder_path, filename)

    try:
        image = Image.open(file.stream)
        try:
            resample = Image.Resampling.LANCZOS
        except AttributeError:
            resample = Image.LANCZOS
        image.thumbnail(max_size, resample)

        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")
        image.save(filepath)
        return filename
    except Exception as e:
        app.logger.exception("Error processing image: %s", e)
        return None

# -------------------------
# Context processor
# -------------------------
@app.context_processor
def inject_globals():
    now = datetime.utcnow()
    current_user = None
    cart_count = 0
    user_id = session.get('user_id')
    if user_id:
        try:
            user = User.query.get(user_id)
            if user:
                current_user = {'id': user.id, 'username': user.username, 'user_type': user.user_type}
                cart_count = CartItem.query.filter_by(user_id=user_id).count()
        except Exception:
            app.logger.exception("Error fetching current_user/cart_count")
    return {'now': now, 'current_user': current_user, 'cart_count': cart_count}

# -------------------------
# Auth routes
# -------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        user_type = request.form.get('user_type', 'customer')

        if not username or not email or not password:
            flash('All fields are required.', 'error')
            return render_template('register.html')

        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists. Please choose a different one.', 'error')
            return render_template('register.html')

        if User.query.filter_by(email=email).first():
            flash('Email already registered. Please use a different email.', 'error')
            return render_template('register.html')

        # Create new user
        new_user = User(username=username, email=email, user_type=user_type)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Please provide username and password.', 'error')
            return render_template('login.html')

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['user_type'] = user.user_type

            flash('Login successful!', 'success')

            # Redirect based on user type
            if user.user_type == 'admin':
                return redirect(url_for('admin'))
            else:
                return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# -------------------------
# Cart and wishlist routes
# -------------------------
@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    if 'user_id' not in session:
        flash('Please login to add items to your cart.', 'error')
        return redirect(url_for('login'))

    product = Product.query.get_or_404(product_id)

    # Check if item already in cart
    cart_item = CartItem.query.filter_by(user_id=session['user_id'], product_id=product_id).first()

    if cart_item:
        cart_item.quantity += 1
    else:
        cart_item = CartItem(user_id=session['user_id'], product_id=product_id, quantity=1)
        db.session.add(cart_item)

    db.session.commit()
    flash(f'{product.name} added to cart!', 'success')
    return redirect(url_for('cart'))

@app.route('/remove_from_cart/<int:item_id>')
def remove_from_cart(item_id):
    if 'user_id' not in session:
        flash('Please login to manage your cart.', 'error')
        return redirect(url_for('login'))

    cart_item = CartItem.query.get_or_404(item_id)

    # Check if user owns this cart item
    if cart_item.user_id != session['user_id']:
        flash('You cannot remove this item.', 'error')
        return redirect(url_for('cart'))

    db.session.delete(cart_item)
    db.session.commit()
    flash('Item removed from cart.', 'success')
    return redirect(url_for('cart'))

@app.route('/update_cart/<int:item_id>', methods=['POST'])
def update_cart(item_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login first.'})

    cart_item = CartItem.query.get_or_404(item_id)

    # Check if user owns this cart item
    if cart_item.user_id != session['user_id']:
        return jsonify({'success': False, 'message': 'Invalid request.'})

    data = request.get_json(silent=True) or {}
    quantity = data.get('quantity', 1)
    try:
        quantity = int(quantity)
    except (ValueError, TypeError):
        quantity = 1

    if quantity <= 0:
        db.session.delete(cart_item)
    else:
        cart_item.quantity = quantity

    db.session.commit()
    return jsonify({'success': True, 'message': 'Cart updated.'})

@app.route('/add_to_wishlist/<int:product_id>')
def add_to_wishlist(product_id):
    if 'user_id' not in session:
        flash('Please login to add items to your wishlist.', 'error')
        return redirect(url_for('login'))

    product = Product.query.get_or_404(product_id)

    # Check if item already in wishlist
    wishlist_item = WishlistItem.query.filter_by(user_id=session['user_id'], product_id=product_id).first()

    if not wishlist_item:
        wishlist_item = WishlistItem(user_id=session['user_id'], product_id=product_id)
        db.session.add(wishlist_item)
        db.session.commit()
        flash(f'{product.name} added to wishlist!', 'success')
    else:
        flash(f'{product.name} is already in your wishlist.', 'info')

    return redirect(url_for('wishlist'))

@app.route('/remove_from_wishlist/<int:item_id>')
def remove_from_wishlist(item_id):
    if 'user_id' not in session:
        flash('Please login to manage your wishlist.', 'error')
        return redirect(url_for('login'))

    wishlist_item = WishlistItem.query.get_or_404(item_id)

    # Check if user owns this wishlist item
    if wishlist_item.user_id != session['user_id']:
        flash('You cannot remove this item.', 'error')
        return redirect(url_for('wishlist'))

    db.session.delete(wishlist_item)
    db.session.commit()
    flash('Item removed from wishlist.', 'success')
    return redirect(url_for('wishlist'))

# -------------------------
# Checkout routes
# -------------------------
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'user_id' not in session:
        flash('Please login to checkout.', 'error')
        return redirect(url_for('login'))

    user_id = session['user_id']
    cart_items = CartItem.query.filter_by(user_id=user_id).all()

    if not cart_items:
        flash('Your cart is empty.', 'error')
        return redirect(url_for('cart'))

    if request.method == 'POST':
        payment_method = request.form.get('payment_method', 'credit_card')

        # Create orders for each cart item
        total_amount = 0
        for item in cart_items:
            order = Order(
                user_id=user_id,
                product_id=item.product_id,
                quantity=item.quantity,
                payment_method=payment_method,
                total_amount=(item.product.price or 0.0) * item.quantity
            )
            db.session.add(order)
            total_amount += order.total_amount

        # Create notifications for admins
        admins = User.query.filter_by(user_type='admin').all()
        for admin in admins:
            notification = Notification(
                admin_id=admin.id,
                message=f"New order placed by {session.get('username', 'Unknown')} for ${total_amount:.2f}"
            )
            db.session.add(notification)

        # Clear cart
        CartItem.query.filter_by(user_id=user_id).delete()

        db.session.commit()
        flash('Order placed successfully!', 'success')
        return redirect(url_for('index'))

    # Calculate total
    total = sum((item.product.price or 0.0) * item.quantity for item in cart_items)

    return render_template('checkout.html', cart_items=cart_items, total=total)

# -------------------------
# Main site routes
# -------------------------
@app.route('/')
def index():
    sections = {s.section_name: s.visible for s in SectionVisibility.query.all()}
    products = Product.query.filter_by(visible=True).all()
    testimonials = Testimonial.query.filter_by(visible=True).all()
    videos = Video.query.filter_by(visible=True).all()
    giveaway = Giveaway.query.filter_by(visible=True).first()

    # cart_count is injected by context_processor (cart_count)
    return render_template(
        'index.html',
        sections=sections,
        products=products,
        testimonials=testimonials,
        videos=videos,
        giveaway=giveaway
    )

@app.route('/cart')
def cart():
    if 'user_id' not in session:
        flash('Please login to view your cart.', 'error')
        return redirect(url_for('login'))

    user_id = session['user_id']
    cart_items = CartItem.query.filter_by(user_id=user_id).all()

    # Calculate total
    total = sum((item.product.price or 0.0) * item.quantity for item in cart_items)

    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/wishlist')
def wishlist():
    if 'user_id' not in session:
        flash('Please login to view your wishlist.', 'error')
        return redirect(url_for('login'))

    user_id = session['user_id']
    wishlist_items = WishlistItem.query.filter_by(user_id=user_id).all()

    return render_template('wishlist.html', wishlist_items=wishlist_items)

# -------------------------
# API endpoints for forms
# -------------------------
@app.route('/api/subscribe', methods=['POST'])
def subscribe():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400

        email = data.get('email')
        if email:
            # Check if email already exists
            existing = Subscriber.query.filter_by(email=email).first()
            if not existing:
                new_sub = Subscriber(email=email)
                db.session.add(new_sub)
                db.session.commit()
                return jsonify({'success': True, 'message': 'Subscribed successfully!'})
            return jsonify({'success': False, 'message': 'Email already subscribed.'})
        return jsonify({'success': False, 'message': 'Email is required.'}), 400
    except Exception as e:
        app.logger.exception("subscribe error")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@app.route('/api/contact', methods=['POST'])
def contact():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400

        name = data.get('name')
        email = data.get('email')
        message_text = data.get('message')

        if name and email and message_text:
            new_message = Message(name=name, email=email, message=message_text)
            db.session.add(new_message)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Message sent successfully!'})
        return jsonify({'success': False, 'message': 'All fields are required.'}), 400
    except Exception as e:
        app.logger.exception("contact error")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@app.route('/api/enter-giveaway', methods=['POST'])
def enter_giveaway():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400

        email = data.get('email')
        if email:
            # In a real implementation, you'd save this to a separate table
            return jsonify({'success': True, 'message': 'Entered giveaway successfully!'})
        return jsonify({'success': False, 'message': 'Email is required.'}), 400
    except Exception as e:
        app.logger.exception("enter_giveaway error")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

# -------------------------
# Admin routes
# -------------------------
@app.route('/admin')
def admin():
    if 'user_id' not in session or session.get('user_type') != 'admin':
        flash('Admin access required.', 'error')
        return redirect(url_for('login'))

    # Get notifications for this admin
    notifications = Notification.query.filter_by(admin_id=session['user_id']).order_by(Notification.created_at.desc()).all()

    # Mark notifications as read (only those fetched)
    for notification in notifications:
        if not notification.is_read:
            notification.is_read = True

    db.session.commit()

    return render_template('admin.html', notifications=notifications)

@app.route('/api/admin/sections', methods=['GET', 'POST'])
def manage_sections():
    try:
        if request.method == 'GET':
            sections = SectionVisibility.query.all()
            return jsonify([s.to_dict() for s in sections])

        if request.method == 'POST':
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'message': 'No data provided'}), 400

            for section_data in data:
                section = SectionVisibility.query.filter_by(section_name=section_data['section_name']).first()
                if section:
                    section.visible = section_data['visible']
            db.session.commit()
            return jsonify({'success': True, 'message': 'Section visibility updated.'})
    except Exception as e:
        app.logger.exception("manage_sections error")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@app.route('/api/admin/products', methods=['GET', 'POST', 'PUT', 'DELETE'])
def manage_products():
    try:
        if request.method == 'GET':
            products = Product.query.all()
            return jsonify([p.to_dict() for p in products])

        if request.method == 'POST':
            name = request.form.get('name')
            description = request.form.get('description')
            details = request.form.get('details')
            price = request.form.get('price')
            visible = request.form.get('visible') == 'true'

            image = None
            if 'image' in request.files:
                image = save_image(request.files['image'], 'products')

            new_product = Product(
                name=name,
                description=description,
                details=details,
                price=float(price) if price else 0.0,
                image=image,
                visible=visible
            )
            db.session.add(new_product)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Product added successfully.'})

        if request.method == 'PUT':
            product_id = request.form.get('id')
            product = Product.query.get(product_id)
            if product:
                product.name = request.form.get('name')
                product.description = request.form.get('description')
                product.details = request.form.get('details')
                product.price = float(request.form.get('price')) if request.form.get('price') else product.price
                product.visible = request.form.get('visible') == 'true'

                if 'image' in request.files and request.files['image'].filename:
                    # Delete old image if exists
                    if product.image:
                        old_image = os.path.join(app.config['UPLOAD_FOLDER'], 'products', product.image)
                        if os.path.exists(old_image):
                            os.remove(old_image)

                    # Save new image
                    product.image = save_image(request.files['image'], 'products')

                db.session.commit()
                return jsonify({'success': True, 'message': 'Product updated successfully.'})
            return jsonify({'success': False, 'message': 'Product not found.'}), 404

        if request.method == 'DELETE':
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'message': 'No data provided'}), 400

            product_id = data.get('id')
            product = Product.query.get(product_id)
            if product:
                # Delete associated image
                if product.image:
                    image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'products', product.image)
                    if os.path.exists(image_path):
                        os.remove(image_path)

                db.session.delete(product)
                db.session.commit()
                return jsonify({'success': True, 'message': 'Product deleted successfully.'})
            return jsonify({'success': False, 'message': 'Product not found.'}), 404
    except Exception as e:
        app.logger.exception("manage_products error")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

# -------------------------
# Serve uploaded files
# -------------------------
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    # Prevent empty filename
    if not filename:
        return jsonify({'success': False, 'message': 'Filename required'}), 400

    # send_from_directory handles subpaths in filename safely
    upload_dir = app.config.get('UPLOAD_FOLDER', 'static/uploads')
    return send_from_directory(upload_dir, filename)

# -------------------------
# Error handlers
# -------------------------
@app.errorhandler(404)
def not_found(error):
    # If request expects HTML, render an HTML page, otherwise JSON
    if request.accept_mimetypes.accept_html:
        return render_template('404.html'), 404
    return jsonify({'success': False, 'message': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    app.logger.exception("Internal server error")
    if request.accept_mimetypes.accept_html:
        return render_template('500.html'), 500
    return jsonify({'success': False, 'message': 'Internal server error'}), 500

# -------------------------
# Debug helper
# -------------------------
@app.route('/debug-products')
def debug_products():
    products = Product.query.filter_by(visible=True).all()
    sections = {s.section_name: s.visible for s in SectionVisibility.query.all()}

    # Return raw HTML without any CSS/JS
    return f"""
    <html><body>
        <h1>DEBUG: Raw Products Data</h1>
        <p>Products found: {len(products)}</p>
        <p>Products section visible: {sections.get('products', False)}</p>
        <hr>
        {"".join(f'<div><h3>{p.name}</h3><p>{p.description}</p><hr></div>' for p in products)}
    </body></html>
    """

@app.route('/api/cart/count')
def get_cart_count():
    if 'user_id' not in session:
        return jsonify({'count': 0})
    
    count = CartItem.query.filter_by(user_id=session['user_id']).count()
    return jsonify({'count': count})

@app.route('/api/admin/stats')
def admin_stats():
    if 'user_id' not in session or session.get('user_type') != 'admin':
        abort(403)
    try:
        page_views = 0  # Placeholder: Implement page view tracking if desired
        orders = Order.query.count()
        users = User.query.count()
        subscribers = Subscriber.query.count()
        unread_messages = Message.query.filter_by(read=False).count()

        return jsonify({
            'page_views': page_views,
            'orders': orders,
            'users': users,
            'subscribers': subscribers,
            'unread_messages': unread_messages
        })
    except Exception as e:
        app.logger.exception("Failed to retrieve admin stats")
        return jsonify({'error': str(e)}), 500


@app.route('/api/admin/messages', methods=['GET', 'DELETE'])
def admin_messages():
    if 'user_id' not in session or session.get('user_type') != 'admin':
        abort(403)

    if request.method == 'GET':
        limit = request.args.get('limit', type=int)
        messages_query = Message.query.order_by(Message.created_at.desc())
        if limit:
            messages_query = messages_query.limit(limit)
        messages = messages_query.all()
        return jsonify([m.to_dict() for m in messages])

    if request.method == 'DELETE':
        data = request.get_json()
        if not data or 'id' not in data:
            return jsonify({'success': False, 'message': 'ID required'}), 400
        message = Message.query.get(data['id'])
        if message:
            db.session.delete(message)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Message deleted'})
        return jsonify({'success': False, 'message': 'Message not found'}), 404


@app.route('/api/admin/subscribers', methods=['GET', 'DELETE'])
def admin_subscribers():
    if 'user_id' not in session or session.get('user_type') != 'admin':
        abort(403)
    if request.method == 'GET':
        subscribers = Subscriber.query.order_by(Subscriber.created_at.desc()).all()
        return jsonify([s.to_dict() for s in subscribers])
    if request.method == 'DELETE':
        data = request.get_json()
        if not data or 'id' not in data:
            return jsonify({'success': False, 'message': 'ID required'}), 400
        subscriber = Subscriber.query.get(data['id'])
        if subscriber:
            db.session.delete(subscriber)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Subscriber deleted'})
        return jsonify({'success': False, 'message': 'Subscriber not found'}), 404


@app.route('/api/admin/videos', methods=['GET', 'POST', 'PUT', 'DELETE'])
def admin_videos():
    if 'user_id' not in session or session.get('user_type') != 'admin':
        abort(403)

    if request.method == 'GET':
        videos = Video.query.order_by(Video.created_at.desc()).all()
        return jsonify([v.to_dict() for v in videos])

    if request.method in ['POST', 'PUT']:
        vid_id = request.form.get('id')
        title = request.form.get('title')
        description = request.form.get('description')
        video_url = request.form.get('video_url')

        # Handle thumbnail upload
        thumbnail_filename = None
        if 'thumbnail' in request.files and request.files['thumbnail'].filename:
            thumbnail_filename = save_image(request.files['thumbnail'], 'videos')

        if request.method == 'POST':
            new_video = Video(title=title, description=description, video_url=video_url, thumbnail=thumbnail_filename)
            db.session.add(new_video)
        else:
            video = Video.query.get(vid_id)
            if not video:
                return jsonify({'success': False, 'message': 'Video not found'}), 404
            video.title = title
            video.description = description
            video.video_url = video_url
            if thumbnail_filename:
                # Delete old thumbnail if exists
                old_thumb_path = os.path.join(app.config['UPLOAD_FOLDER'], 'videos', video.thumbnail) if video.thumbnail else None
                if old_thumb_path and os.path.exists(old_thumb_path):
                    os.remove(old_thumb_path)
                video.thumbnail = thumbnail_filename
        db.session.commit()
        return jsonify({'success': True, 'message': 'Video saved successfully'})

    if request.method == 'DELETE':
        data = request.get_json()
        if not data or 'id' not in data:
            return jsonify({'success': False, 'message': 'ID required'}), 400
        video = Video.query.get(data['id'])
        if video:
            if video.thumbnail:
                thumb_path = os.path.join(app.config['UPLOAD_FOLDER'], 'videos', video.thumbnail)
                if os.path.exists(thumb_path):
                    os.remove(thumb_path)
            db.session.delete(video)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Video deleted'})
        return jsonify({'success': False, 'message': 'Video not found'}), 404


@app.route('/api/admin/giveaway', methods=['GET', 'POST', 'PUT', 'DELETE'])
def admin_giveaway():
    if 'user_id' not in session or session.get('user_type') != 'admin':
        abort(403)

    # Note: Assumes only one active giveaway (can be adjusted)
    current = Giveaway.query.first()

    if request.method == 'GET':
        if current:
            data = current.to_dict()
            # Add participants count if you have participants table logic
            data['participants_count'] = 0
            return jsonify(data)
        return jsonify({})

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')

        image_filename = None
        if 'image' in request.files and request.files['image'].filename:
            image_filename = save_image(request.files['image'], 'giveaway')

        if current:
            # Update existing giveaway
            current.title = title
            current.description = description
            if image_filename:
                old_img_path = os.path.join(app.config['UPLOAD_FOLDER'], 'giveaway', current.image)
                if current.image and os.path.exists(old_img_path):
                    os.remove(old_img_path)
                current.image = image_filename
        else:
            # Create new giveaway
            current = Giveaway(title=title, description=description, image=image_filename)
            db.session.add(current)

        db.session.commit()
        return jsonify({'success': True, 'message': 'Giveaway updated successfully'})

    if request.method == 'DELETE':
        if current:
            if current.image:
                img_path = os.path.join(app.config['UPLOAD_FOLDER'], 'giveaway', current.image)
                if os.path.exists(img_path):
                    os.remove(img_path)
            db.session.delete(current)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Giveaway deleted'})
        return jsonify({'success': False, 'message': 'No giveaway to delete'}), 404


if __name__ == '__main__':
    # Ensure secret key is set (from Config)
    if not app.config.get('SECRET_KEY'):
        app.config['SECRET_KEY'] = os.urandom(24)

    app.run(debug=True, host='0.0.0.0', port=5000)
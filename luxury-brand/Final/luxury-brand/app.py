from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from PIL import Image
import io
from datetime import datetime

# Import config and database models
from config import Config
from database import db, Product, Testimonial, Video, Giveaway, Subscriber, Message, SectionVisibility

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

db.init_app(app)

# Initialize database with default sections
with app.app_context():
    db.create_all()
    
    # Create default section visibility settings if they don't exist
    sections = ['products', 'testimonials', 'giveaway', 'videos', 'contact', 'socials']
    for section in sections:
        if not SectionVisibility.query.filter_by(section_name=section).first():
            db.session.add(SectionVisibility(section_name=section, visible=True))
    db.session.commit()

# Helper function for image upload
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def save_image(file, folder, max_size=(800, 800)):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], folder, filename)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Open and process image
        try:
            image = Image.open(file.stream)
            # Use Resampling.LANCZOS for newer Pillow versions
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Save image
            image.save(filepath)
            return filename
        except Exception as e:
            print(f"Error processing image: {e}")
            return None
    return None

# Routes for main website
@app.route('/')
def index():
    sections = {s.section_name: s.visible for s in SectionVisibility.query.all()}
    products = Product.query.filter_by(visible=True).all()
    testimonials = Testimonial.query.filter_by(visible=True).all()
    videos = Video.query.filter_by(visible=True).all()
    giveaway = Giveaway.query.filter_by(visible=True).first()
    
    return render_template('index.html', 
                         sections=sections,
                         products=products,
                         testimonials=testimonials,
                         videos=videos,
                         giveaway=giveaway)

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
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

# Routes for admin dashboard
@app.route('/admin')
def admin():
    return render_template('admin.html')

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
                price=float(price),
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
                product.price = float(request.form.get('price'))
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
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

# Additional API endpoints would follow the same pattern...

# Serve uploaded files
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'message': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'message': 'Internal server error'}), 500

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

@app.route('/cart')
def cart():
    return render_template('cart.html')

@app.route('/wishlist')
def wishlist():
    return render_template('wishlist.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

    

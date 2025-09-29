# fix_images.py
from app import app, db
from database import Product, Giveaway, Video

def fix_image_references():
    with app.app_context():
        # Update product images
        products = Product.query.all()
        for product in products:
            if product.image and not product.image.startswith('http'):
                # Remove the image reference if file doesn't exist
                import os
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'products', product.image)
                if not os.path.exists(image_path):
                    product.image = None
        db.session.commit()
        print("Fixed product image references")

if __name__ == '__main__':
    fix_image_references()
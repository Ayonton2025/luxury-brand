from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


# ------------------------
# MODELS
# ------------------------

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    details = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(200), nullable=True)  # extended path
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    visible = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "details": self.details,
            "price": self.price,
            "image": self.image,
            "visible": self.visible,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Testimonial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    video_url = db.Column(db.String(300), nullable=True)
    image = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    visible = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            "id": self.id,
            "author": self.author,
            "content": self.content,
            "video_url": self.video_url,
            "image": self.image,
            "visible": self.visible,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    video_url = db.Column(db.String(300), nullable=False)
    thumbnail = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    visible = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "video_url": self.video_url,
            "thumbnail": self.thumbnail,
            "visible": self.visible,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Giveaway(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    image = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    visible = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "image": self.image,
            "visible": self.visible,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Subscriber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "message": self.message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "read": self.read,
        }


class SectionVisibility(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    section_name = db.Column(db.String(50), nullable=False, unique=True)
    visible = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            "id": self.id,
            "section_name": self.section_name, 
            "visible": self.visible
        }


# ------------------------
# USER + AUTH
# ------------------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    user_type = db.Column(db.String(20), default="customer")  # "customer" or "admin"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    orders = db.relationship("Order", backref="user", lazy=True)
    notifications = db.relationship("Notification", backref="user", lazy=True)
    cart_items = db.relationship("CartItem", backref="user", lazy=True)
    wishlist_items = db.relationship("WishlistItem", backref="user", lazy=True)
    payments = db.relationship("Payment", backref="user", lazy=True)

    # Password methods
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "user_type": self.user_type,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    status = db.Column(db.String(20), default="pending")  # pending, completed, cancelled, refunded
    payment_method = db.Column(db.String(50), nullable=True)
    total_amount = db.Column(db.Float, nullable=False, default=0.0)
    payment_status = db.Column(db.String(20), default="pending")  # pending, paid, failed, refunded
    shipping_address = db.Column(db.Text, nullable=True)
    billing_address = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    order_items = db.relationship("OrderItem", backref="order", lazy=True, cascade="all, delete-orphan")
    payments = db.relationship("Payment", backref="order", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "status": self.status,
            "payment_method": self.payment_method,
            "total_amount": self.total_amount,
            "payment_status": self.payment_status,
            "shipping_address": self.shipping_address,
            "billing_address": self.billing_address,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "order_items": [item.to_dict() for item in self.order_items]
        }


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)
    price = db.Column(db.Float, nullable=False)  # Price at time of purchase

    # Relationship
    product = db.relationship("Product", backref="order_items")

    def to_dict(self):
        return {
            "id": self.id,
            "order_id": self.order_id,
            "product_id": self.product_id,
            "product_name": self.product.name if self.product else None,
            "quantity": self.quantity,
            "price": self.price,
            "subtotal": self.price * self.quantity
        }


class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)  # 'stripe', 'paypal', etc.
    payment_intent_id = db.Column(db.String(100), nullable=True)  # For Stripe/PayPal transaction ID
    payment_status = db.Column(db.String(20), default='pending')  # pending, completed, failed, refunded
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='USD')
    transaction_data = db.Column(db.Text, nullable=True)  # Raw response from payment gateway
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'user_id': self.user_id,
            'payment_method': self.payment_method,
            'payment_intent_id': self.payment_intent_id,
            'payment_status': self.payment_status,
            'amount': self.amount,
            'currency': self.currency,
            'transaction_data': self.transaction_data,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    notification_type = db.Column(db.String(50), default="general")  # order, payment, system, etc.
    related_id = db.Column(db.Integer, nullable=True)  # ID of related order, payment, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "message": self.message,
            "is_read": self.is_read,
            "notification_type": self.notification_type,
            "related_id": self.related_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    product = db.relationship("Product", backref="cart_items")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "product_id": self.product_id,
            "product_name": self.product.name if self.product else None,
            "product_price": self.product.price if self.product else None,
            "product_image": self.product.image if self.product else None,
            "quantity": self.quantity,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class WishlistItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship("Product", backref="wishlist_items")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "product_id": self.product_id,
            "product_name": self.product.name if self.product else None,
            "product_price": self.product.price if self.product else None,
            "product_image": self.product.image if self.product else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# ------------------------
# DB INITIALIZER
# ------------------------

def init_db():
    """Initialize database with default values."""
    db.create_all()

    # Create default admin user
    if not User.query.filter_by(user_type="admin").first():
        admin = User(username="admin", email="admin@luxury.com", user_type="admin")
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()

    # Create default section visibility entries
    sections = ["products", "testimonials", "videos", "giveaway", "contact", "socials"]
    for section in sections:
        if not SectionVisibility.query.filter_by(section_name=section).first():
            db.session.add(SectionVisibility(section_name=section, visible=True))

    # Add sample products if none exist
    if Product.query.count() == 0:
        sample_products = [
            Product(
                name="Premium Watch",
                description="Elegant luxury watch with precision movement.",
                details="Stainless steel case, sapphire crystal, water resistant up to 100m",
                price=299.99,
                visible=True
            ),
            Product(
                name="Leather Handbag",
                description="Handcrafted genuine leather handbag.",
                details="Made from premium Italian leather, multiple compartments, gold hardware",
                price=199.99,
                visible=True
            )
        ]
        for product in sample_products:
            db.session.add(product)
    
    # Add sample testimonials if none exist
    if Testimonial.query.count() == 0:
        sample_testimonials = [
            Testimonial(
                author="Sarah Johnson",
                content="The quality of these products is exceptional. I'm a customer for life!",
                visible=True
            ),
            Testimonial(
                author="Michael Chen",
                content="Fast shipping and excellent customer service. Will definitely shop here again.",
                visible=True
            )
        ]
        for testimonial in sample_testimonials:
            db.session.add(testimonial)
    
    # Add sample videos if none exist
    if Video.query.count() == 0:
        sample_videos = [
            Video(
                title="Crafting The Luxury Watch",
                description="See how our master watchmakers create precision timepieces.",
                video_url="https://www.youtube.com/embed/dQw4w9WgXcQ",
                visible=True
            ),
            Video(
                title="Leather Artistry",
                description="Follow the process of creating our premium leather goods.",
                video_url="https://www.youtube.com/embed/dQw4w9WgXcQ",
                visible=True
            )
        ]
        for video in sample_videos:
            db.session.add(video)
    
    # Add sample giveaway if none exist
    if Giveaway.query.count() == 0:
        from datetime import timedelta
        giveaway_end_date = datetime.utcnow() + timedelta(days=7)
        giveaway = Giveaway(
            title="Win Our Premium Collection",
            description="Enter for a chance to win our luxury products!",
            end_date=giveaway_end_date,
            visible=True
        )
        db.session.add(giveaway)
    
    db.session.commit()
    print("Database initialized successfully!")
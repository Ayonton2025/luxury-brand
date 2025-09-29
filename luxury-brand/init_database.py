from datetime import datetime, timedelta
from app import app, db
from database import (
    User, Product, Testimonial, Video, Giveaway, 
    Subscriber, Message, SectionVisibility, 
    Order, OrderItem, CartItem, WishlistItem, Notification, Payment
)
from werkzeug.security import generate_password_hash

def init_database():
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # --- SECTION VISIBILITY ---
        sections = [
            ('products', True),
            ('testimonials', True),
            ('giveaway', True),
            ('videos', True),
            ('contact', True),
            ('socials', True)
        ]
        
        for section_name, visible in sections:
            if not SectionVisibility.query.filter_by(section_name=section_name).first():
                section = SectionVisibility(section_name=section_name, visible=visible)
                db.session.add(section)
        
        # --- USERS ---
        if not User.query.filter_by(user_type="admin").first():
            admin = User(
                username="admin", 
                email="admin@luxury.com", 
                user_type="admin"
            )
            admin.set_password("admin123")
            db.session.add(admin)
        
        if not User.query.filter_by(username="johndoe").first():
            customer = User(
                username="johndoe", 
                email="johndoe@example.com", 
                user_type="customer"
            )
            customer.set_password("customer123")
            db.session.add(customer)
        
        # --- SUBSCRIBERS ---
        subscribers = [
            "subscriber1@example.com",
            "subscriber2@example.com",
        ]
        
        for email in subscribers:
            if not Subscriber.query.filter_by(email=email).first():
                subscriber = Subscriber(email=email)
                db.session.add(subscriber)
        
        # --- MESSAGES ---
        messages = [
            ("Alice Smith", "alice@example.com", "I love your products!"),
            ("Bob Lee", "bob@example.com", "Could you add more leather bags?"),
        ]
        
        for name, email, message_text in messages:
            if not Message.query.filter_by(email=email, message=message_text).first():
                message = Message(name=name, email=email, message=message_text)
                db.session.add(message)
        
        # --- PRODUCTS ---
        products = [
            ('Luxury Watch Series X',
             'Handcrafted timepiece with sapphire crystal and automatic movement.',
             'Swiss automatic movement, 42mm case, water resistant to 100m, genuine leather strap.',
             2499.99, 'watch.jpg', True),
            ('Artisan Leather Bag',
             'Hand-stitched premium leather bag with brass hardware.',
             'Full-grain leather, brass fixtures, internal laptop compartment, lifetime warranty.',
             899.99, 'bag.jpg', True)
        ]
        
        for name, description, details, price, image, visible in products:
            if not Product.query.filter_by(name=name).first():
                product = Product(
                    name=name,
                    description=description,
                    details=details,
                    price=price,
                    image=image,
                    visible=visible
                )
                db.session.add(product)
        
        # --- TESTIMONIALS ---
        testimonials = [
            ('Sarah Johnson', "The craftsmanship on my luxury watch is exceptional. I've received countless compliments and the precision is remarkable.",
             None, 'testimonial1.jpg', True),
            ('Michael Chen', "This leather bag exceeded my expectations. The quality is evident in every stitch, and it just gets better with age.",
             'https://www.youtube.com/embed/dQw4w9WgXcQ', None, True),
            ('Emma Rodriguez', "I've owned many luxury items, but the attention to detail in these products is truly in a class of its own.",
             None, 'testimonial3.jpg', True)
        ]
        
        for author, content, video_url, image, visible in testimonials:
            if not Testimonial.query.filter_by(author=author, content=content).first():
                testimonial = Testimonial(
                    author=author,
                    content=content,
                    video_url=video_url,
                    image=image,
                    visible=visible
                )
                db.session.add(testimonial)
        
        # --- VIDEOS ---
        videos = [
            ('Crafting The Luxury Watch', 'See how our master watchmakers create precision timepieces.',
             'https://www.youtube.com/embed/dQw4w9WgXcQ', 'video1_thumb.jpg', True),
            ('Leather Artistry', 'Follow the process of creating our premium leather goods.',
             'https://www.youtube.com/embed/dQw4w9WgXcQ', 'video2_thumb.jpg', True),
            ('Style Guide', 'How to incorporate our products into your everyday style.',
             'https://www.youtube.com/embed/dQw4w9WgXcQ', 'video3_thumb.jpg', True)
        ]
        
        for title, description, video_url, thumbnail, visible in videos:
            if not Video.query.filter_by(title=title).first():
                video = Video(
                    title=title,
                    description=description,
                    video_url=video_url,
                    thumbnail=thumbnail,
                    visible=visible
                )
                db.session.add(video)
        
        # --- GIVEAWAY ---
        if not Giveaway.query.first():
            giveaway_end_date = datetime.utcnow() + timedelta(days=7)
            giveaway = Giveaway(
                title='Win Our Premium Collection',
                description='Enter for a chance to win both our luxury watch and artisan leather bag, valued at over $3,000.',
                end_date=giveaway_end_date,
                image='giveaway.jpg',
                visible=True
            )
            db.session.add(giveaway)
        
        # Commit all changes first to get IDs
        db.session.commit()
        
        # Get the customer user
        customer_user = User.query.filter_by(username="johndoe").first()
        admin_user = User.query.filter_by(username="admin").first()
        
        # Get products
        watch_product = Product.query.filter_by(name="Luxury Watch Series X").first()
        bag_product = Product.query.filter_by(name="Artisan Leather Bag").first()
        
        if customer_user and watch_product:
            # --- SAMPLE ORDER ---
            if not Order.query.filter_by(user_id=customer_user.id).first():
                order = Order(
                    user_id=customer_user.id,
                    status="pending",
                    payment_method="credit_card",
                    total_amount=2499.99,
                    shipping_address="123 Customer Street, City, State 12345",
                    billing_address="123 Customer Street, City, State 12345"
                )
                db.session.add(order)
                db.session.flush()  # Get order ID without committing
                
                # Add order item
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=watch_product.id,
                    quantity=1,
                    price=watch_product.price
                )
                db.session.add(order_item)
                
                # --- SAMPLE PAYMENT ---
                payment = Payment(
                    order_id=order.id,
                    user_id=customer_user.id,
                    payment_method="stripe",
                    payment_intent_id="pi_sample_123",
                    payment_status="pending",
                    amount=2499.99,
                    currency="USD"
                )
                db.session.add(payment)
            
            # --- SAMPLE CART ITEM ---
            if not CartItem.query.filter_by(user_id=customer_user.id).first():
                cart_item = CartItem(
                    user_id=customer_user.id,
                    product_id=bag_product.id,
                    quantity=1
                )
                db.session.add(cart_item)
            
            # --- SAMPLE WISHLIST ITEM ---
            if not WishlistItem.query.filter_by(user_id=customer_user.id).first():
                wishlist_item = WishlistItem(
                    user_id=customer_user.id,
                    product_id=watch_product.id
                )
                db.session.add(wishlist_item)
        
        if admin_user:
            # --- SAMPLE NOTIFICATION ---
            if not Notification.query.first():
                notification = Notification(
                    user_id=admin_user.id,
                    message="New customer John Doe placed an order.",
                    notification_type="order",
                    is_read=False
                )
                db.session.add(notification)
        
        # Final commit
        db.session.commit()
        print("Database initialized with sample data!")

if __name__ == '__main__':
    init_database()
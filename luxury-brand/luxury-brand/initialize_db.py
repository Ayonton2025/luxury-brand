import sqlite3
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash


def initialize_database():
    # Connect to SQLite database (created if doesn't exist)
    conn = sqlite3.connect('luxury_products.db')
    cursor = conn.cursor()

    # --- SECTION VISIBILITY ---
    sections = [
        ('products', True),
        ('testimonials', True),
        ('giveaway', True),
        ('videos', True),
        ('contact', True),
        ('socials', True)
    ]
    cursor.executemany(
        'INSERT OR IGNORE INTO section_visibility (section_name, visible) VALUES (?, ?)',
        sections
    )

    # --- USERS ---
    admin_password = generate_password_hash("admin123")
    cursor.execute('''INSERT OR IGNORE INTO user (username, email, password_hash, user_type, created_at) 
                     VALUES (?, ?, ?, ?, ?)''',
                   ("admin", "admin@luxury.com", admin_password, "admin", datetime.now()))

    customer_password = generate_password_hash("customer123")
    cursor.execute('''INSERT OR IGNORE INTO user (username, email, password_hash, user_type, created_at) 
                     VALUES (?, ?, ?, ?, ?)''',
                   ("johndoe", "johndoe@example.com", customer_password, "customer", datetime.now()))

    # --- SUBSCRIBERS ---
    subscribers = [
        ("subscriber1@example.com", datetime.now()),
        ("subscriber2@example.com", datetime.now()),
    ]
    cursor.executemany(
        '''INSERT OR IGNORE INTO subscriber (email, created_at) VALUES (?, ?)''', subscribers
    )

    # --- MESSAGES ---
    messages = [
        ("Alice Smith", "alice@example.com", "I love your products!", False, datetime.now()),
        ("Bob Lee", "bob@example.com", "Could you add more leather bags?", False, datetime.now()),
    ]
    cursor.executemany(
        '''INSERT INTO message (name, email, message, read, created_at) VALUES (?, ?, ?, ?, ?)''', messages
    )

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
    cursor.executemany(
        '''INSERT OR IGNORE INTO product (name, description, details, price, image, visible) 
           VALUES (?, ?, ?, ?, ?, ?)''',
        products
    )

    # --- TESTIMONIALS ---
    testimonials = [
        ('Sarah Johnson', "The craftsmanship on my luxury watch is exceptional. I've received countless compliments and the precision is remarkable.",
         None, 'testimonial1.jpg', True),
        ('Michael Chen', "This leather bag exceeded my expectations. The quality is evident in every stitch, and it just gets better with age.",
         'https://www.youtube.com/embed/dQw4w9WgXcQ', None, True),
        ('Emma Rodriguez', "I've owned many luxury items, but the attention to detail in these products is truly in a class of its own.",
         None, 'testimonial3.jpg', True)
    ]
    cursor.executemany(
        '''INSERT OR IGNORE INTO testimonial (author, content, video_url, image, visible) 
           VALUES (?, ?, ?, ?, ?)''',
        testimonials
    )

    # --- VIDEOS ---
    videos = [
        ('Crafting The Luxury Watch', 'See how our master watchmakers create precision timepieces.',
         'https://www.youtube.com/embed/dQw4w9WgXcQ', 'video1_thumb.jpg', True),
        ('Leather Artistry', 'Follow the process of creating our premium leather goods.',
         'https://www.youtube.com/embed/dQw4w9WgXcQ', 'video2_thumb.jpg', True),
        ('Style Guide', 'How to incorporate our products into your everyday style.',
         'https://www.youtube.com/embed/dQw4w9WgXcQ', 'video3_thumb.jpg', True)
    ]
    cursor.executemany(
        '''INSERT OR IGNORE INTO video (title, description, video_url, thumbnail, visible) 
           VALUES (?, ?, ?, ?, ?)''',
        videos
    )

    # --- GIVEAWAY ---
    giveaway_end_date = datetime.now() + timedelta(days=7)
    cursor.execute(
        '''INSERT OR IGNORE INTO giveaway (title, description, end_date, image, visible) 
           VALUES (?, ?, ?, ?, ?)''',
        ('Win Our Premium Collection',
         'Enter for a chance to win both our luxury watch and artisan leather bag, valued at over $3,000.',
         giveaway_end_date, 'giveaway.jpg', True)
    )

    # --- SAMPLE ORDER ---
    cursor.execute(
        '''INSERT OR IGNORE INTO "order" (user_id, product_id, quantity, status, payment_method, total_amount, created_at) 
           VALUES (?, ?, ?, ?, ?, ?, ?)''',
        (2, 1, 1, "pending", "credit_card", 2499.99, datetime.now())
    )

    # --- SAMPLE CART ITEM ---
    cursor.execute(
        '''INSERT OR IGNORE INTO cart_item (user_id, product_id, quantity, created_at) 
           VALUES (?, ?, ?, ?)''',
        (2, 2, 1, datetime.now())
    )

    # --- SAMPLE WISHLIST ITEM ---
    cursor.execute(
        '''INSERT OR IGNORE INTO wishlist_item (user_id, product_id, created_at) 
           VALUES (?, ?, ?)''',
        (2, 1, datetime.now())
    )

    # --- SAMPLE NOTIFICATION ---
    cursor.execute(
        '''INSERT OR IGNORE INTO notification (admin_id, message, is_read, created_at) 
           VALUES (?, ?, ?, ?)''',
        (1, "New customer John Doe placed an order.", False, datetime.now())
    )

    # Commit changes and close the connection
    conn.commit()
    conn.close()

    print("Database initialized with sample data!")


if __name__ == '__main__':
    initialize_database()

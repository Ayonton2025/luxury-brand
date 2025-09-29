import sqlite3
from datetime import datetime, timedelta

def initialize_database():
    # Connect to SQLite database (will be created if it doesn't exist)
    conn = sqlite3.connect('luxury_products.db')
    cursor = conn.cursor()
    
    # Insert default section visibility settings
    sections = [
        ('products', True),
        ('testimonials', True),
        ('giveaway', True),
        ('videos', True),
        ('contact', True),
        ('socials', True)
    ]
    
    cursor.executemany('INSERT OR IGNORE INTO section_visibility (section_name, visible) VALUES (?, ?)', sections)
    
    # Insert sample products
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
    
    cursor.executemany('''INSERT INTO product (name, description, details, price, image, visible) 
                       VALUES (?, ?, ?, ?, ?, ?)''', products)
    
    # Insert sample testimonials
    testimonials = [
        ('Sarah Johnson', 'The craftsmanship on my luxury watch is exceptional. I\'ve received countless compliments and the precision is remarkable.', 
         None, 'testimonial1.jpg', True),
        ('Michael Chen', 'This leather bag exceeded my expectations. The quality is evident in every stitch, and it just gets better with age.', 
         'https://www.youtube.com/embed/dQw4w9WgXcQ', None, True),
        ('Emma Rodriguez', 'I\'ve owned many luxury items, but the attention to detail in these products is truly in a class of its own.', 
         None, 'testimonial3.jpg', True)
    ]
    
    cursor.executemany('''INSERT INTO testimonial (author, content, video_url, image, visible) 
                       VALUES (?, ?, ?, ?, ?)''', testimonials)
    
    # Insert sample videos
    videos = [
        ('Crafting The Luxury Watch', 'See how our master watchmakers create precision timepieces.',
         'https://www.youtube.com/embed/dQw4w9WgXcQ', 'video1_thumb.jpg', True),
        ('Leather Artistry', 'Follow the process of creating our premium leather goods.',
         'https://www.youtube.com/embed/dQw4w9WgXcQ', 'video2_thumb.jpg', True),
        ('Style Guide', 'How to incorporate our products into your everyday style.',
         'https://www.youtube.com/embed/dQw4w9WgXcQ', 'video3_thumb.jpg', True)
    ]
    
    cursor.executemany('''INSERT INTO video (title, description, video_url, thumbnail, visible) 
                       VALUES (?, ?, ?, ?, ?)''', videos)
    
    # Insert sample giveaway
    giveaway_end_date = datetime.now() + timedelta(days=7)
    cursor.execute('''INSERT INTO giveaway (title, description, end_date, image, visible) 
                   VALUES (?, ?, ?, ?, ?)''', 
                   ('Win Our Premium Collection', 
                    'Enter for a chance to win both our luxury watch and artisan leather bag, valued at over $3,000.',
                    giveaway_end_date, 'giveaway.jpg', True))
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print("Database initialized with sample data!")

if __name__ == '__main__':
    initialize_database()
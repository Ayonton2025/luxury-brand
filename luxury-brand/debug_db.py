from app import app, db
from database import Product, SectionVisibility

with app.app_context():
    print("=== DATABASE DEBUG INFO ===")
    
    # Check section visibility
    sections = SectionVisibility.query.all()
    print("Section Visibility:")
    for section in sections:
        print(f"  {section.section_name}: {section.visible}")
    
    # Check products
    products = Product.query.all()
    print(f"\nProducts in database: {len(products)}")
    for product in products:
        print(f"  {product.name} - Visible: {product.visible}")
    
    print("\n=== END DEBUG ===")
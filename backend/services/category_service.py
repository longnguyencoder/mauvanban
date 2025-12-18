"""
Category service for managing document categories
"""
from models import db, Category
from sqlalchemy import func


class CategoryService:
    """Service for category operations"""
    
    @staticmethod
    def get_all_categories(include_inactive=False):
        """
        Get all categories as a flat list
        
        Args:
            include_inactive: Include inactive categories
            
        Returns:
            list: List of categories
        """
        query = Category.query
        
        if not include_inactive:
            query = query.filter_by(is_active=True)
        
        return query.order_by(Category.display_order, Category.name).all()
    
    @staticmethod
    def get_category_tree(include_inactive=False):
        """
        Get categories organized in tree structure
        
        Args:
            include_inactive: Include inactive categories
            
        Returns:
            list: List of root categories with nested children
        """
        query = Category.query.filter_by(parent_id=None)
        
        if not include_inactive:
            query = query.filter_by(is_active=True)
        
        root_categories = query.order_by(Category.display_order, Category.name).all()
        
        return [cat.to_dict(include_children=True, include_documents=True) for cat in root_categories]
    
    @staticmethod
    def get_category_by_id(category_id):
        """Get category by ID"""
        return db.session.get(Category, category_id)
    
    @staticmethod
    def get_category_by_slug(slug):
        """Get category by slug"""
        return Category.query.filter_by(slug=slug, is_active=True).first()
    
    @staticmethod
    def create_category(name, description=None, parent_id=None, icon=None, display_order=0):
        try:
            # Handle empty string as None
            if not parent_id:
                parent_id = None

            # Verify parent exists if provided
            if parent_id:
                parent = db.session.get(Category, parent_id)
                if not parent:
                    return None, 'Parent category not found'
            
            # Generate unique slug
            from slugify import slugify
            base_slug = slugify(name)
            slug = base_slug
            counter = 1
            
            while Category.query.filter_by(slug=slug).first():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            category = Category(
                name=name,
                description=description,
                parent_id=parent_id,
                icon=icon,
                display_order=display_order,
                slug=slug  # Set explicitly
            )
            # category.generate_slug() # Removed model method call
            
            db.session.add(category)
            db.session.commit()
            
            return category, None
            
        except Exception as e:
            db.session.rollback()
            return None, f'Failed to create category: {str(e)}'
    
    @staticmethod
    def update_category(category_id, name=None, description=None, parent_id=None, 
                       icon=None, display_order=None, is_active=None):
        """
        Update category
        
        Args:
            category_id: Category ID
            name: New name
            description: New description
            parent_id: New parent ID
            icon: New icon
            display_order: New display order
            is_active: New active status
            
        Returns:
            tuple: (category, error_message)
        """
        try:
            category = db.session.get(Category, category_id)
            
            if not category:
                return None, 'Category not found'
            
            # Check for circular reference if updating parent
            if parent_id and parent_id != category.parent_id:
                if parent_id == category_id:
                    return None, 'Category cannot be its own parent'
                
                # Check if new parent is a descendant
                parent = db.session.get(Category, parent_id)
                if parent:
                    current = parent
                    while current.parent_id:
                        if current.parent_id == category_id:
                            return None, 'Cannot create circular reference'
                        current = db.session.get(Category, current.parent_id)
            
            # Update fields
            if name is not None and name != category.name:
                category.name = name
                # Regenerate slug
                from slugify import slugify
                base_slug = slugify(name)
                slug = base_slug
                counter = 1
                
                # Check uniqueness (excluding self)
                while Category.query.filter(Category.slug == slug, Category.id != category_id).first():
                    slug = f"{base_slug}-{counter}"
                    counter += 1
                category.slug = slug
            elif name is not None:
                category.name = name # Update name but keep slug if same name (rare case or just ensuring)
            
            if description is not None:
                category.description = description
            if parent_id is not None:
                category.parent_id = parent_id
            if icon is not None:
                category.icon = icon
            if display_order is not None:
                category.display_order = display_order
            if is_active is not None:
                category.is_active = is_active
            
            db.session.commit()
            
            return category, None
            
        except Exception as e:
            db.session.rollback()
            return None, f'Failed to update category: {str(e)}'
    
    @staticmethod
    def delete_category(category_id):
        """
        Delete category (soft delete by setting is_active=False)
        
        Args:
            category_id: Category ID
            
        Returns:
            tuple: (success, error_message)
        """
        try:
            category = db.session.get(Category, category_id)
            
            if not category:
                return False, 'Category not found'
            
            # Check if category has documents
            if len(category.documents) > 0:
                return False, 'Cannot delete category with documents'
            
            # Soft delete
            category.is_active = False
            db.session.commit()
            
            return True, None
            
        except Exception as e:
            db.session.rollback()
            return False, f'Failed to delete category: {str(e)}'
    
    @staticmethod
    def reorder_categories(category_orders):
        """
        Reorder categories
        
        Args:
            category_orders: List of {id, display_order} dicts
            
        Returns:
            tuple: (success, error_message)
        """
        try:
            for item in category_orders:
                category = db.session.get(Category, item['id'])
                if category:
                    category.display_order = item['display_order']
            
            db.session.commit()
            return True, None
            
        except Exception as e:
            db.session.rollback()
            return False, f'Failed to reorder categories: {str(e)}'

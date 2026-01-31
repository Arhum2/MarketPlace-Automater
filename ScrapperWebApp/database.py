"""
Database connection and operations for Supabase.
"""
import os
from typing import Optional, Dict, Any, List
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class Database:
    """Database service for Supabase operations."""
    
    def __init__(self):
        """Initialize Supabase client."""
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_ANON_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError(
                "Missing Supabase credentials. "
                "Please set SUPABASE_URL and SUPABASE_ANON_KEY in your .env file"
            )
        
        self.client: Client = create_client(supabase_url, supabase_key)
        self._test_connection()
    
    def _test_connection(self):
        """Test the database connection."""
        try:
            # Simple query to test connection
            self.client.table("products").select("id").limit(1).execute()
        except Exception as e:
            # If products table doesn't exist yet, that's okay
            # We'll create it with the schema
            if "relation" in str(e).lower() and "does not exist" in str(e).lower():
                print("⚠️  Products table doesn't exist yet. Run database_schema.sql first.")
            else:
                raise ConnectionError(f"Failed to connect to Supabase: {e}")
    
    # ========== PRODUCT OPERATIONS ==========
    
    def create_product(self, url: str, **kwargs) -> Dict[str, Any]:
        """Create a new product."""
        data = {
            "url": url,
            **kwargs
        }
        result = self.client.table("products").insert(data).execute()
        return result.data[0] if result.data else None
    
    def get_product(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Get a product by ID."""
        result = self.client.table("products").select("*").eq("id", product_id).execute()
        return result.data[0] if result.data else None
    
    def get_product_by_url(self, url: str) -> Optional[Dict[str, Any]]:
        """Get a product by URL."""
        result = self.client.table("products").select("*").eq("url", url).execute()
        return result.data[0] if result.data else None
    
    def list_products(self, status: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """List all products, optionally filtered by status."""
        query = self.client.table("products").select("*")
        
        if status:
            query = query.eq("status", status)
        
        result = query.order("created_at", desc=True).limit(limit).execute()
        return result.data if result.data else []
    
    def update_product(self, product_id: str, **kwargs) -> Dict[str, Any]:
        """Update a product."""
        result = self.client.table("products").update(kwargs).eq("id", product_id).execute()
        return result.data[0] if result.data else None
    
    def update_product_status(self, product_id: str, status: str) -> Dict[str, Any]:
        """Update product status."""
        return self.update_product(product_id, status=status)
    
    # ========== JOB OPERATIONS ==========
    
    def create_job(self, product_id: str, job_type: str, **kwargs) -> Dict[str, Any]:
        """Create a new job."""
        data = {
            "product_id": product_id,
            "job_type": job_type,
            **kwargs
        }
        result = self.client.table("jobs").insert(data).execute()
        return result.data[0] if result.data else None
    
    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get a job by ID."""
        result = self.client.table("jobs").select("*").eq("id", job_id).execute()
        return result.data[0] if result.data else None
    
    def get_jobs_by_product(self, product_id: str) -> List[Dict[str, Any]]:
        """Get all jobs for a product."""
        result = self.client.table("jobs").select("*").eq("product_id", product_id).order("created_at", desc=True).execute()
        return result.data if result.data else []
    
    def update_job(self, job_id: str, **kwargs) -> Dict[str, Any]:
        """Update a job."""
        result = self.client.table("jobs").update(kwargs).eq("id", job_id).execute()
        return result.data[0] if result.data else None
    
    def update_job_status(self, job_id: str, status: str, error: Optional[str] = None) -> Dict[str, Any]:
        """Update job status."""
        update_data = {"status": status}
        if error:
            update_data["error"] = error
        if status in ["completed", "failed"]:
            from datetime import datetime
            update_data["completed_at"] = datetime.utcnow().isoformat()
        return self.update_job(job_id, **update_data)
    
    # ========== IMAGE OPERATIONS ==========
    
    def add_product_image(self, product_id: str, file_path: str, image_order: int = 0) -> Dict[str, Any]:
        """Add an image to a product."""
        data = {
            "product_id": product_id,
            "file_path": file_path,
            "image_order": image_order
        }
        result = self.client.table("product_images").insert(data).execute()
        return result.data[0] if result.data else None
    
    def get_product_images(self, product_id: str) -> List[Dict[str, Any]]:
        """Get all images for a product."""
        result = self.client.table("product_images").select("*").eq("product_id", product_id).order("image_order").execute()
        return result.data if result.data else []
    
    # ========== STORAGE OPERATIONS ==========

    def upload_image(self, product_id: str, image_path: str, image_order: int = 0) -> Optional[str]:
        """
        Upload an image to Supabase Storage and save reference in product_images table.
        Returns the public URL of the uploaded image.
        """
        import os

        # Read the file
        if not os.path.exists(image_path):
            print(f"Image not found: {image_path}")
            return None

        # Create storage path: product_images/{product_id}/{filename}
        filename = os.path.basename(image_path)
        storage_path = f"{product_id}/{filename}"

        try:
            # Upload to Supabase Storage (bucket: "product-images")
            with open(image_path, "rb") as f:
                file_data = f.read()

            result = self.client.storage.from_("product-images").upload(
                path=storage_path,
                file=file_data,
                file_options={"content-type": "image/jpeg"}
            )

            # Get the public URL
            public_url = self.client.storage.from_("product-images").get_public_url(storage_path)

            # Save to product_images table
            self.add_product_image(product_id, public_url, image_order)

            return public_url

        except Exception as e:
            print(f"Failed to upload image: {e}")
            return None

    def upload_product_images(self, product_id: str, image_paths: List[str]) -> List[str]:
        """Upload multiple images for a product. Returns list of public URLs."""
        urls = []
        for i, path in enumerate(image_paths):
            url = self.upload_image(product_id, path, image_order=i)
            if url:
                urls.append(url)
                print(f"  Uploaded image {i+1}/{len(image_paths)}")
        return urls

    # ========== POSTING HISTORY OPERATIONS ==========
    
    def create_posting_history(self, product_id: str, status: str, marketplace_url: Optional[str] = None, error: Optional[str] = None) -> Dict[str, Any]:
        """Create a posting history entry."""
        data = {
            "product_id": product_id,
            "status": status,
            "marketplace_url": marketplace_url,
            "error": error
        }
        result = self.client.table("posting_history").insert(data).execute()
        return result.data[0] if result.data else None
    
    def get_posting_history(self, product_id: str) -> List[Dict[str, Any]]:
        """Get posting history for a product."""
        result = self.client.table("posting_history").select("*").eq("product_id", product_id).order("posted_at", desc=True).execute()
        return result.data if result.data else []


# Global database instance
_db_instance: Optional[Database] = None

def get_db() -> Database:
    """Get or create database instance (singleton pattern)."""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance

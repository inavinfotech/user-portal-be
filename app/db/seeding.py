from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine
from app.models.auth import Role, Permission
from app.models.user import User
from app.core.security import get_password_hash
from app.core.config import settings
from app.models.base import Base

def seed_db():
    db = SessionLocal()
    try:
        # 1. Create Default Permissions
        default_permissions = [
            {"name": "Read Users", "resource": "users", "action": "read", "description": "View user profiles and lists"},
            {"name": "Write Users", "resource": "users", "action": "write", "description": "Create and update users"},
            {"name": "Delete Users", "resource": "users", "action": "delete", "description": "Remove users from system"},
            {"name": "Read Roles", "resource": "roles", "action": "read", "description": "View role tiers"},
            {"name": "Write Roles", "resource": "roles", "action": "write", "description": "Manage role configurations"},
            {"name": "Read Permissions", "resource": "permissions", "action": "read", "description": "View access control nodes"},
            {"name": "Write Permissions", "resource": "permissions", "action": "write", "description": "Manage permission registry"},
            {"name": "Read Applications", "resource": "applications", "action": "read", "description": "View registered applications"},
            {"name": "Write Applications", "resource": "applications", "action": "write", "description": "Register and manage applications"},
            {"name": "Read Sessions", "resource": "sessions", "action": "read", "description": "Monitor active security sessions"},
        ]

        created_perms = []
        for perm_data in default_permissions:
            perm = db.query(Permission).filter(
                Permission.resource == perm_data["resource"],
                Permission.action == perm_data["action"]
            ).first()
            if not perm:
                perm = Permission(**perm_data)
                db.add(perm)
                db.flush()
            created_perms.append(perm)

        # 2. Create Admin Role
        admin_role = db.query(Role).filter(Role.name == "admin").first()
        if not admin_role:
            admin_role = Role(name="admin", description="Full system access (Root Tier)")
            db.add(admin_role)
            db.flush()
        
        # 3. Assign all perms to admin role
        for perm in created_perms:
            if perm not in admin_role.permissions:
                admin_role.permissions.append(perm)

        # 4. Create Admin User
        admin_user = db.query(User).filter(User.email == settings.ADMIN_EMAIL).first()
        if not admin_user:
            admin_user = User(
                email=settings.ADMIN_EMAIL,
                full_name="System Administrator",
                hashed_password=get_password_hash(settings.ADMIN_PASSWORD),
                is_active=True
            )
            admin_user.roles.append(admin_role)
            db.add(admin_user)
        else:
            if admin_role not in admin_user.roles:
                admin_user.roles.append(admin_role)
        
        db.commit()
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

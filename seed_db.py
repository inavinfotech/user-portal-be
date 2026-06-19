import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "app"))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine
from app.models.auth import Role, Permission
from app.models.user import User
from app.core.security import get_password_hash
from app.models.base import Base
from app.core.config import settings

def seed():
    # Create tables
    Base.metadata.create_all(bind=engine)
    
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
                print(f"Created permission: {perm.resource}:{perm.action}")
            created_perms.append(perm)

        # 2. Create Default Roles
        admin_role = db.query(Role).filter(Role.name == "admin").first()
        if not admin_role:
            admin_role = Role(name="admin", description="Full system access (Root Tier)")
            db.add(admin_role)
            db.flush()
            print("Created admin role")

        learner_role = db.query(Role).filter(Role.name == "learner").first()
        if not learner_role:
            learner_role = Role(name="learner", description="LMS student/learner access role")
            db.add(learner_role)
            db.flush()
            print("Created learner role")

        consumer_role = db.query(Role).filter(Role.name == "consumer").first()
        if not consumer_role:
            consumer_role = Role(name="consumer", description="Main website consumer/customer role")
            db.add(consumer_role)
            db.flush()
            print("Created consumer role")
        
        # 3. Assign all perms to admin role
        for perm in created_perms:
            if perm not in admin_role.permissions:
                admin_role.permissions.append(perm)
                print(f"Assigned {perm.resource}:{perm.action} to admin role")

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
            print(f"Created admin user: {settings.ADMIN_EMAIL}")
        else:
            if admin_role not in admin_user.roles:
                admin_user.roles.append(admin_role)
                print(f"Assigned admin role to existing user {settings.ADMIN_EMAIL}")
        
        db.commit()
        print("\nDatabase seeded successfully!")
        print(f"Administrator: {settings.ADMIN_EMAIL}")
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed()

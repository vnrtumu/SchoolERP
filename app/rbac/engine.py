from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.rbac.models import RoleModel, PermissionModel
from app.rbac.constants import Role, ROLE_PERMISSIONS


class PermissionEngine:
    """Permission evaluation and enforcement engine"""
    
    async def check_user_permissions(
        self,
        db: AsyncSession,
        user,
        required_permissions: List[str]
    ) -> bool:
        """
        Check if user has all required permissions.
        
        Args:
            db: Database session
            user: User object with roles
            required_permissions: List of permission codes
        
        Returns:
            True if user has all permissions, False otherwise
        """
        # Super admins bypass all checks
        if hasattr(user, "role") and user.role == Role.SUPER_ADMIN:
            return True
        
        # Get user's permissions through their roles
        user_permissions = await self.get_user_permissions(db, user)
        
        # Check if all required permissions are present
        return all(perm in user_permissions for perm in required_permissions)
    
    async def get_user_permissions(
        self,
        db: AsyncSession,
        user
    ) -> List[str]:
        """
        Get all permissions for a user through their assigned roles.
        
        Returns:
            List of permission codes
        """
        # For simple role-based users (single role in user.role)
        if hasattr(user, "role"):
            role = user.role
            if role in ROLE_PERMISSIONS:
                return [str(p.value) for p in ROLE_PERMISSIONS[role]]
        
        # For multi-role users (roles relationship)
        if hasattr(user, "roles"):
            # Load roles with permissions
            result = await db.execute(
                select(RoleModel)
                .options(selectinload(RoleModel.permissions))
                .where(RoleModel.id.in_([r.id for r in user.roles]))
            )
            roles = result.scalars().all()
            
            # Collect all permissions from all roles
            permissions = set()
            for role in roles:
                for perm in role.permissions:
                    permissions.add(perm.code)
            
            return list(permissions)
        
        return []
    
    async def has_permission(
        self,
        db: AsyncSession,
        user,
        permission_code: str
    ) -> bool:
        """Check if user has a specific permission"""
        permissions = await self.get_user_permissions(db, user)
        return permission_code in permissions
    
    async def seed_permissions(self, db: AsyncSession):
        """
        Seed default permissions into database.
        Called during tenant provisioning.
        """
        from app.rbac.constants import Permission
        
        for perm in Permission:
            parts = perm.value.split(".")
            module = parts[0] if len(parts) > 0 else "general"
            resource = parts[1] if len(parts) > 1 else "all"
            action = parts[2] if len(parts) > 2 else "access"
            
            # Check if permission exists
            result = await db.execute(
                select(PermissionModel).where(PermissionModel.code == perm.value)
            )
            existing = result.scalar_one_or_none()
            
            if not existing:
                perm_model = PermissionModel(
                    code=perm.value,
                    module=module,
                    resource=resource,
                    action=action,
                    description=f"{action.title()} {resource} in {module}"
                )
                db.add(perm_model)
        
        await db.commit()
    
    async def seed_roles(self, db: AsyncSession):
        """
        Seed default roles with permissions.
        Called during tenant provisioning.
        """
        from app.rbac.constants import Role, ROLE_PERMISSIONS
        
        # First ensure permissions exist
        await self.seed_permissions(db)
        
        # Create roles with their permissions
        for role, perms in ROLE_PERMISSIONS.items():
            # Check if role exists
            result = await db.execute(
                select(RoleModel).where(RoleModel.name == role.value)
            )
            existing_role = result.scalar_one_or_none()
            
            if not existing_role:
                # Get permission objects
                perm_codes = [str(p.value) for p in perms]
                perm_result = await db.execute(
                    select(PermissionModel).where(PermissionModel.code.in_(perm_codes))
                )
                permission_objects = perm_result.scalars().all()
                
                # Create role
                role_model = RoleModel(
                    name=role.value,
                    description=f"System role: {role.value}",
                    is_system=True
                )
                role_model.permissions = permission_objects
                db.add(role_model)
        
        await db.commit()

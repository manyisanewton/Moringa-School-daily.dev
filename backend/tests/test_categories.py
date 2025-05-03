import unittest
from app import create_app, db
from app.models import Category, User, Role, UserRole, UserProfile, AuditLog, RefreshToken
import json
from flask_jwt_extended import JWTManager, create_access_token

class TestCategoriesRoutes(unittest.TestCase):
    def setUp(self):
        self.app = create_app(config_class='config.TestConfig')
        self.app.config['TESTING'] = True
        self.app.config['JWT_TOKEN_LOCATION'] = ['headers']
        self.app.config['JWT_HEADER_NAME'] = 'Authorization'
        self.app.config['JWT_HEADER_TYPE'] = 'Bearer'
        self.app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False
        JWTManager(self.app)  # Initialize JWTManager for token creation
        self.client = self.app.test_client()
        with self.app.app_context():
            # Create a user with Admin role
            user = User.query.filter_by(email="admin@test.com").first()
            if not user:
                user = User(email="admin@test.com", password_hash="hashedpassword")
                db.session.add(user)
                db.session.commit()
            
            # Ensure Admin role exists
            admin_role = Role.query.filter_by(name="Admin").first()
            if not admin_role:
                admin_role = Role(name="Admin")
                db.session.add(admin_role)
                db.session.commit()
            
            # Assign Admin role to user
            user_role = UserRole.query.filter_by(user_id=user.id, role_id=admin_role.id).first()
            if not user_role:
                user_role = UserRole(user_id=user.id, role_id=admin_role.id)
                db.session.add(user_role)
                db.session.commit()
            
            # Create a valid token with an integer identity (user.id)
            self.token = create_access_token(identity=user.id)

    def test_create_category(self):
        data = {"name": "DevOps", "description": "DevOps content"}
        response = self.client.post(
            '/categories',
            data=json.dumps(data),
            headers={"Authorization": f"Bearer {self.token}"},
            content_type='application/json'
        )
        print(f"Response status: {response.status_code}, Data: {response.data}")
        self.assertEqual(response.status_code, 201)
        self.assertIn("Category created", str(response.data))

    def tearDown(self):
        with self.app.app_context():
            # Delete related records first to avoid foreign key violations
            db.session.query(RefreshToken).delete()
            db.session.query(AuditLog).delete()
            db.session.query(UserProfile).delete()
            db.session.query(UserRole).delete()
            db.session.query(Category).delete()
            db.session.query(User).delete()
            db.session.query(Role).delete()
            db.session.commit()
            db.session.remove()
            print("Cleaned up database: Users =", User.query.count(), "Roles =", Role.query.count(), "UserRoles =", UserRole.query.count(), "UserProfiles =", UserProfile.query.count(), "AuditLogs =", AuditLog.query.count(), "RefreshTokens =", RefreshToken.query.count(), "Categories =", Category.query.count())

if __name__ == '_main_':
    unittest.main()
    
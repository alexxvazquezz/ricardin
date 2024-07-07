from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, Role, Employee
from itsdangerous import URLSafeSerializer as Serializer
from config import Config
import time
import logging

bp = Blueprint('api', __name__)
logger = logging.getLogger(__name__)

@bp.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    phone_number = data.get('phone_number')

    if not email or not password:
        return jsonify({'error': 'Email and password required.'}), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered.'}), 400

    new_user = User(email=email, password=password, first_name=first_name, last_name=last_name, phone_number=phone_number)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully.', 'user': new_user.to_dict()}), 201

@bp.route('/register_employee', methods=['POST'])
def register_employee():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    phone_number = data.get('phone_number')
    social_security = data.get('social_security')

    # Assign default values here
    employee_type = 'full-time'  # Default value
    hourly_wage = 0.0  # Default value

    if not email or not password or not social_security:
        return jsonify({'error': 'Email, password, and social security required.'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered.'}), 400

    employee_role = Role.query.filter_by(name='employee').first()
    new_user = User(email=email, password=password, first_name=first_name, last_name=last_name, phone_number=phone_number, role=employee_role)

    db.session.add(new_user)
    db.session.commit()

    new_employee = Employee(user=new_user, social_security=social_security, employee_type=employee_type, hourly_wage=hourly_wage)

    db.session.add(new_employee)
    db.session.commit()

    return jsonify({'message': 'Employee registered successfully.', 'user': new_user.to_dict(), 'employee': new_employee.to_dict()}), 201

@bp.route('/employees', methods=['GET'])
@login_required
def get_employees():
    user = User.query.get(current_user.id)

    if not user.is_authenticated or user.role.name != 'admin':
        return jsonify({'error': 'Unathorized access'}), 403
    
    employees = Employee.query.options(db.joinedload(Employee.user).joinedload(User.role)).all()
    return jsonify([employee.to_dict() for employee in employees]),201


@bp.route('/register_admin', methods=['POST'])
def register_admin():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    phone_number = data.get('phone_number')

    if not email or not password:
        return jsonify({'error': 'Email and password required.'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered.'}), 400

    admin_role = Role.query.filter_by(name='admin').first()
    new_user = User(email=email, password=password, first_name=first_name, last_name=last_name, phone_number=phone_number, role=admin_role)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'Admin registered successfully.', 'user': new_user.to_dict()}), 201

@bp.route('/register_customer', methods=['POST'])
def register_customer():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    phone_number = data.get('phone_number')

    if not email or not password:
        return jsonify({'error': 'Email and password required.'}),400
    
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered.'}), 400
    
    customer_role = Role.query.filter_by(name='customer').first()
    if not customer_role:
        return jsonify({'error': 'Customer role not found.'})
    
    new_user = User(email=email, password=password, first_name=first_name, last_name=last_name, phone_number=phone_number, role=customer_role)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'Customer registered successfully.', 'user': new_user.to_dict()}), 201

@bp.route('/get_customers', methods=['GET'])
def get_customers():
    customers = User.query.filter_by(role_id=Role.query.filter_by(name='customer').first().id).all()

    customers_data = [customer.to_dict() for customer in customers]

    return jsonify(customers_data), 200 

@bp.route('/modify_employee', methods=['PUT'])
@login_required
def modify_employee():
    try:
        data = request.json
        employee_id = data.get('employee_id')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        phone_number = data.get('phone_number')
        employee_type = data.get('employee_type')
        hourly_wage = data.get('hourly_wage')

        logger.debug(f"Received data: {data}")

        user = User.query.get(current_user.id)

        if not user.is_authenticated or user.role.name != 'admin':
            return jsonify({'error': 'Only admins can modify employee details.'}), 403

        employee = Employee.query.get(employee_id)
        if not employee:
            return jsonify({'error': 'Employee not found.'}), 404

        if first_name:
            employee.user.first_name = first_name
        if last_name:
            employee.user.last_name = last_name
        if phone_number:
            employee.user.phone_number = phone_number
        if employee_type is not None:
            employee.employee_type = employee_type
        if hourly_wage is not None:
            employee.hourly_wage = hourly_wage

        db.session.commit()
        logger.debug("Employee details updated successfully.")
        return jsonify({'message': 'Employee details updated successfully', 'employee': employee.to_dict()}), 200

    except Exception as e:
        logger.error(f"Error modifying employee: {str(e)}")
        return jsonify({'error': 'An error occurred while modifying the employee.'})
    
    
@bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password required.'}), 400
    
    user = User.query.filter_by(email=email).options(db.joinedload(User.role)).first()

    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid email or password.'}), 401
    
    login_user(user)

    # Generate access token
    s = Serializer(Config.SECRET_KEY)
    expiration_time = int(time.time()) + 3600
    token = s.dumps({'user_id': user.id, 'expires': expiration_time})

    return jsonify({'message': 'Login successful.', 'access_token': token}), 200

@bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'messsage': 'Logout successful.'}), 200

@bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    return jsonify({
        'id': current_user.id,
        'email': current_user.email,
        'first_name': current_user.first_name,
        'last_name': current_user.last_name
    })

@bp.route('/users', methods=['GET'])
@login_required
def get_all_users():
    users = User.query.all()
    return jsonify({'users': [user.to_dict() for user in users]}), 200


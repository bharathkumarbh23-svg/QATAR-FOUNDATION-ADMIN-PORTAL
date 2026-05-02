import re

VALID_CATEGORIES = {'Technology', 'Business', 'Design', 'Marketing', 'Data Science', 'Other'}


def is_valid_email(email: str) -> bool:
    """Basic RFC-style email check."""
    return bool(re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email))


def validate_signup(data: dict) -> dict:
    """
    Validate signup payload.
    Returns a dict of field -> error message (empty dict = valid).
    """
    errors = {}

    full_name        = (data.get('full_name') or '').strip()
    email            = (data.get('email') or '').strip()
    password         = data.get('password') or ''
    confirm_password = data.get('confirm_password') or ''

    if not full_name:
        errors['full_name'] = 'Full name is required.'
    if not email or not is_valid_email(email):
        errors['email'] = 'A valid email address is required.'
    if len(password) < 8:
        errors['password'] = 'Password must be at least 8 characters.'
    if password != confirm_password:
        errors['confirm_password'] = 'Passwords do not match.'

    return errors


def validate_opportunity(data: dict) -> tuple[dict, dict]:
    """
    Validate and clean opportunity payload.
    Returns (cleaned_data, errors_dict).
    """
    errors = {}

    name               = (data.get('name')                 or '').strip()
    duration           = (data.get('duration')             or '').strip()
    start_date         = (data.get('start_date')           or '').strip()
    description        = (data.get('description')          or '').strip()
    skills_raw         = (data.get('skills')               or '').strip()
    category           = (data.get('category')             or '').strip()
    future_opps        = (data.get('future_opportunities') or '').strip()
    max_applicants_raw = (data.get('max_applicants')       or '').strip() \
                         if isinstance(data.get('max_applicants'), str) \
                         else str(data.get('max_applicants') or '')

    if not name:          errors['name']                 = 'Opportunity name is required.'
    if not duration:      errors['duration']             = 'Duration is required.'
    if not start_date:    errors['start_date']           = 'Start date is required.'
    if not description:   errors['description']          = 'Description is required.'
    if not skills_raw:    errors['skills']               = 'At least one skill is required.'
    if not future_opps:   errors['future_opportunities'] = 'Future opportunities field is required.'

    if not category:
        errors['category'] = 'Category is required.'
    elif category not in VALID_CATEGORIES:
        errors['category'] = f'Category must be one of: {", ".join(sorted(VALID_CATEGORIES))}.'

    max_applicants = None
    raw = max_applicants_raw.strip()
    if raw:
        try:
            max_applicants = int(raw)
            if max_applicants < 1:
                errors['max_applicants'] = 'Maximum applicants must be a positive number.'
        except ValueError:
            errors['max_applicants'] = 'Maximum applicants must be a whole number.'

    cleaned = {
        'name':                 name,
        'duration':             duration,
        'start_date':           start_date,
        'description':          description,
        'skills':               skills_raw,
        'category':             category,
        'future_opportunities': future_opps,
        'max_applicants':       max_applicants,
    }
    return cleaned, errors

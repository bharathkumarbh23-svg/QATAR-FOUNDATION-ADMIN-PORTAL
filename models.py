from datetime import datetime
from extensions import db


class Admin(db.Model):
    """Registered admin account."""
    __tablename__ = 'admins'

    id            = db.Column(db.Integer, primary_key=True)
    full_name     = db.Column(db.String(150), nullable=False)
    email         = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    opportunities = db.relationship(
        'Opportunity', backref='admin', lazy=True, cascade='all, delete-orphan'
    )
    reset_tokens  = db.relationship(
        'PasswordResetToken', backref='admin', lazy=True, cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f'<Admin {self.email}>'


class Opportunity(db.Model):
    """Opportunity posted by an admin."""
    __tablename__ = 'opportunities'

    id                   = db.Column(db.Integer, primary_key=True)
    admin_id             = db.Column(db.Integer, db.ForeignKey('admins.id'), nullable=False, index=True)

    name                 = db.Column(db.String(200), nullable=False)
    duration             = db.Column(db.String(100), nullable=False)
    start_date           = db.Column(db.String(50),  nullable=False)
    description          = db.Column(db.Text,         nullable=False)
    skills               = db.Column(db.Text,         nullable=False)   # comma-separated
    category             = db.Column(db.String(100),  nullable=False)
    future_opportunities = db.Column(db.Text,         nullable=False)
    max_applicants       = db.Column(db.Integer,      nullable=True)    # optional

    created_at           = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at           = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id':                   self.id,
            'admin_id':             self.admin_id,
            'name':                 self.name,
            'duration':             self.duration,
            'start_date':           self.start_date,
            'description':          self.description,
            'skills':               self.skills,
            'skills_list':          [s.strip() for s in self.skills.split(',') if s.strip()],
            'category':             self.category,
            'future_opportunities': self.future_opportunities,
            'max_applicants':       self.max_applicants,
            'created_at':           self.created_at.isoformat() if self.created_at else None,
            'updated_at':           self.updated_at.isoformat()  if self.updated_at  else None,
        }

    def __repr__(self):
        return f'<Opportunity {self.name}>'


class PasswordResetToken(db.Model):
    """Single-use, time-limited password reset token."""
    __tablename__ = 'password_reset_tokens'

    id         = db.Column(db.Integer, primary_key=True)
    admin_id   = db.Column(db.Integer, db.ForeignKey('admins.id'), nullable=False, index=True)
    token      = db.Column(db.String(100), unique=True, nullable=False, index=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    used       = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<PasswordResetToken admin={self.admin_id} used={self.used}>'

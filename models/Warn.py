import db

class Warn(db.Base):
    __tablename__ = 'warns'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    reason = db.Column(db.String(255))
    
    def __repr__(self):
        return '<Warn %r>' % self.user_id
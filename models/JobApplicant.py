import db

class JobApplicant(db.Base):
    __tablename__ = 'job_applicants'

    post_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    
    def __repr__(self):
        return '<JobApplicant %r>' % self.post_id
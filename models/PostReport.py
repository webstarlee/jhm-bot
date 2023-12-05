import db

class PostReport(db.Base):
    __tablename__ = 'post_reports'

    post_id = db.Column(db.String(50), primary_key=True)
    report_msg = db.Column(db.Integer)
    reported_by = db.Column(db.Integer)
    reported_at = db.Column(db.Integer)
    report_status = db.Column(db.String(50))
    
    def __repr__(self):
        return '<PostReport %r>' % self.post_id
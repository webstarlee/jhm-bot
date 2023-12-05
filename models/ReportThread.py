import db

class ReportThread(db.Base):
    __tablename__ = 'report_threads'

    report_msg = db.Column(db.String(50), primary_key=True)
    channel_id = db.Column(db.Integer)
    thread_id = db.Column(db.Integer)
    
    def __repr__(self):
        return '<ReportThread %r>' % self.report_msg
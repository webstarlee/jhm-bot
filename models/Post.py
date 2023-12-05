import db

class Post(db.Base):
    __tablename__ = 'posts'

    post_id = db.Column(db.String(50), primary_key=True)
    user_id = db.Column(db.Integer)
    posted_at = db.Column(db.Integer)
    post_title = db.Column(db.String(80))
    post_desc = db.Column(db.Text)
    post_portfolio = db.Column(db.String(80))
    post_payment = db.Column(db.String(80))
    post_deadline = db.Column(db.String(80))
    status = db.Column(db.String(80), default="false")
    post_type = db.Column(db.Integer)
    ping_role = db.Column(db.Integer)
    
    def __repr__(self):
        return '<Post %r>' % self.post_id

class IncomingPost(db.Base):
    __tablename__ = 'incoming_posts'

    post_id = db.Column(db.String(50), primary_key=True)
    user_id = db.Column(db.Integer)
    message_id = db.Column(db.Integer)
    
    def __repr__(self):
        return '<IncomingPost %r>' % self.post_id

class OutgoingPost(db.Base):
    __tablename__ = 'outgoing_posts'

    post_id = db.Column(db.String(50), primary_key=True)
    user_id = db.Column(db.Integer)
    message_id = db.Column(db.Integer)
    channel_id = db.Column(db.Integer)
    forum_id = db.Column(db.Integer)
    approved_by = db.Column(db.Integer)
    bumped_at = db.Column(db.Integer)
    
    def __repr__(self):
        return '<OutgoingPost %r>' % self.post_id
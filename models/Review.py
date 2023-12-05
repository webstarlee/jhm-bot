import db

class Review(db.Base):
    __tablename__ = 'reviews'

    review_id = db.Column(db.Integer, primary_key=True)
    freelancer_id = db.Column(db.Integer)
    client_id = db.Column(db.Integer)
    category = db.Column(db.String(80))
    stars = db.Column(db.Integer)
    review = db.Column(db.Text)
    
    def __repr__(self):
        return '<Review %r>' % self.review_id
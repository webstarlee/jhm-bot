import db
import datetime
from models import Post, PostReport, IncomingPost, OutgoingPost, ReportThread, Review

db.Base.metadata.create_all(db.engine)

def init_function():
    print("function initialized")

def insert_for_fire_post(post_id, user_id, post_title, post_desc, post_portfolio, post_payment):
    for_fire_post = Post(
        post_id=post_id,
        user_id=user_id,
        posted_at=round(datetime.datetime.now().timestamp()),
        post_title=post_title,
        post_desc=post_desc,
        post_portfolio=post_portfolio,
        post_payment=post_payment,
        post_type="forhire",
    )
    db.session.add(for_fire_post)
    db.session.commit()

def update_for_fire_post_ping_role(post_id, ping_role):
    post = db.session.query(Post).filter_by(post_id=post_id).one_or_none()
    if post != None:
        post.ping_role = ping_role
        db.session.commit()

def update_for_fire_post_status(post_id, status):
    post = db.session.query(Post).filter_by(post_id=post_id).one_or_none()
    if post != None:
        post.status = status
        db.session.commit()

def find_post_by_post_id(post_id):
    post = db.session.query(Post).filter_by(post_id=post_id).one_or_none()

    return post

def update_for_fire_post(post_id, post_title, post_desc, post_portfolio, post_payment):
    post = db.session.query(Post).filter_by(post_id=post_id).one_or_none()
    if post != None:
        post.post_title = post_title
        post.posted_at = round(datetime.datetime.now().timestamp())
        post.post_desc = post_desc
        post.post_portfolio = post_portfolio
        post.post_payment = post_payment
        db.session.commit()

def insert_out_going_post(post_id, user_id, approver_id, message_id, forum_id):
    out_going_post = OutgoingPost(
        post_id=post_id,
        user_id=user_id,
        approved_by=approver_id,
        message_id=message_id,
        forum_id=forum_id,
        bumped_at=round(datetime.datetime.now().timestamp()),
    )
    db.session.add(out_going_post)
    db.session.commit()

def insert_incoming_post(post_id, user_id, message_id):
    oncoming_post = IncomingPost(
        post_id=post_id,
        user_id=user_id,
        message_id=message_id,
    )
    db.session.add(oncoming_post)
    db.session.commit()

def post_remove(post_id):
    post = db.session.query(Post).filter_by(post_id=post_id).one_or_none()
    if post:
        db.session.delete(post)

def incoming_post_remove(post_id):
    incoming_post = db.session.query(IncomingPost).filter_by(post_id=post_id).one_or_none()
    if incoming_post:
        db.session.delete(incoming_post)

def find_incoming_post(message_id):
    incoming_post = db.session.query(IncomingPost).filter_by(message_id=message_id).one_or_none()
    return incoming_post

def find_out_going_post_by_forum_id(forum_id):
    outgoing_post = db.session.query(OutgoingPost).filter_by(forum_id=forum_id).one_or_none()
    return outgoing_post

def update_out_going_post_bumped_at(forum_id, bumped_at):
    outgoing_post = db.session.query(OutgoingPost).filter_by(forum_id=forum_id).one_or_none()
    if outgoing_post:
        outgoing_post.bumped_at = bumped_at
        db.session.commit()
        
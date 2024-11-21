from app.db import db 
from datetime import datetime

class Media(db.Model):
    __tablename__ = 'media'

    id = db.Column(db.Integer, primary_key=True)
    media_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    file_url = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    thumbnail_url = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'<Media {self.media_name}>'

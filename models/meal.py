from database import db
import datetime

class Meal(db.Model):
  __tablename__ = 'meal'

  id = db.Column(db.Integer, primary_key=True)
  meal_name = db.Column(db.String(80), nullable=False)
  meal_description = db.Column(db.String(255))
  date_time = db.Column(db.DateTime(timezone=True), default=lambda: datetime.datetime.now(datetime.timezone.utc))
  diet_meal = db.Column(db.Boolean, default=True, nullable=False)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

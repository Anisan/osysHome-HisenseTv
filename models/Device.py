from app.database import Column, SurrogatePK, db

class HisenseDevice(SurrogatePK, db.Model):
    __tablename__ = 'hisense_device'
    title = Column(db.String(100))
    ip = Column(db.String(100))
    mac = Column(db.String(100))
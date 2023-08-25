from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
# Baseクラスのインポート
from database import Base

# Userクラスの作成
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    # Userが所持するItemを受け取る
    items = relationship("Item", back_populates="owner")


# Itemクラスの作成
class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    # Userクラスのidカラムを外部キーとして指定する
    owner_id = Column(Integer, ForeignKey("users.id"))
    # ownerのUser情報を受け取る
    owner = relationship("User", back_populates="items")
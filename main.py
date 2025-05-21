from secrets import token_urlsafe

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import (Session, declarative_base, relationship,
                            sessionmaker)

sql_engine = create_engine(
    "postgresql+psycopg2://postgres:@localhost:5432/postgres"
)
SessionLocal = sessionmaker(bind=sql_engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, unique=True)
    email = Column(String, unique=True)
    password = Column(String)
    username = Column(String)
    tokens = relationship("Token", back_populates="user", cascade="all, delete-orphan")


class Token(Base):
    __tablename__ = "tokens"
    token_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    token = Column(String, unique=True)
    user = relationship("User", back_populates="tokens")


Base.metadata.create_all(sql_engine)
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def create_user(username: str, email: str, password: str, db: Session):
    new_user = User(username=username, email=email, password=password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    token_value = token_urlsafe(32)
    token = Token(user_id=new_user.id, token=token_value)
    db.add(token)
    db.commit()
    return token.token


def get_token(email: str, password: str, db: Session):
    user = db.query(User).filter_by(email=email, password=password).first()
    if user:
        token_value = token_urlsafe(32)
        token = Token(user_id=user.id, token=token_value)
        db.add(token)
        db.commit()
        return (token.token, user.username)
    return None


def destroy_token(token: str, db: Session):
    token_obj = db.query(Token).filter_by(token=token).first()
    if token_obj:
        db.delete(token_obj)
        db.commit()
        return True
    return False


def destroy_user(token: str, db: Session):
    token_obj = db.query(Token).filter_by(token=token).first()
    if token_obj:
        user = db.query(User).filter_by(id=token_obj.user_id).first()
        if user:
            db.delete(user)
            db.commit()
            return True
    return False


def modify_password(token: str, new_password: str, db: Session):
    token_obj = db.query(Token).filter_by(token=token).first()
    if token_obj:
        user = db.query(User).filter_by(id=token_obj.user_id).first()
        if user:
            user.password = new_password
            db.commit()
            new_token_value = token_urlsafe(32)
            new_token = Token(user_id=user.id, token=new_token_value)
            db.add(new_token)
            db.commit()
            return new_token.token
    return None


def authenticate(token: str, db: Session):
    token_obj = db.query(Token).filter_by(token=token).first()
    if token_obj:
        user = db.query(User).filter_by(id=token_obj.user_id).first()
        if user:
            return (user.email, user.username)
    return None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def auth(token: str, db: Session = Depends(get_db)):
    auth_obj = authenticate(token, db)
    if auth_obj:
        return {"email": auth_obj[0], "user_name": auth_obj[1]}
    raise HTTPException(status_code=401, detail="Invalid auth token")


@app.post("/signup")
def signup(username: str, email: str, password: str, db: Session = Depends(get_db)):
    token = create_user(username, email, password, db)
    if token:
        return {"token": token}
    raise HTTPException(status_code=400, detail="Error creating user")


@app.post("/login")
def login(email: str, password: str, db: Session = Depends(get_db)):
    login_obj = get_token(email, password, db)
    if login_obj:
        return {"token": login_obj[0], "user_name": login_obj[1]}
    raise HTTPException(status_code=401, detail="Invalid email or password")


@app.post("/change-password")
def change_password(token: str, new_password: str, db: Session = Depends(get_db)):
    new_token = modify_password(token, new_password, db)
    if new_token:
        return {"token": new_token}
    raise HTTPException(status_code=400, detail="Error changing password")


@app.post("/logout")
def logout(token: str, db: Session = Depends(get_db)):
    if destroy_token(token, db):
        return {"status": 0}
    raise HTTPException(status_code=400, detail="Invalid token")


@app.delete("/delete-account")
def delete_account(token: str, db: Session = Depends(get_db)):
    if destroy_user(token, db):
        return {"status": 0}
    raise HTTPException(status_code=400, detail="Invalid token or user not found")

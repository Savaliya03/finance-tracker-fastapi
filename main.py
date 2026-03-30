from fastapi import FastAPI, Depends, HTTPException, status, Query
from sqlalchemy import create_engine, Column, Integer, String, desc, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from datetime import date
from typing import Optional

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# SQLAlchemy Models
class Users(Base):
    __tablename__ = "Users"

    id = Column(Integer, primary_key=True, nullable=False, index=True)
    username = Column(String, index=True, unique=True)
    password = Column(String(200))

class Transaction(Base):
    __tablename__ = "Transaction"

    id = Column(Integer, primary_key=True, index=True)
    user = Column(String)
    name = Column(String)
    amount = Column(Float)
    type = Column(String)
    category = Column(String)
    date = Column(Date)
    description = Column(String)

# Create tables
Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI()

# Pydantic models
class UserCreate(BaseModel):
    username: str
    password: str

class TokenData(BaseModel):
    username: str | None = None

class TransactionCreate(BaseModel):
    name: str
    amount: float
    type: str
    category: str
    date: date
    description: str

class SummaryResponse(BaseModel):
    total_income: float
    total_expense: float
    net_balance: float
    category_breakdown: list[dict]
    monthly_trends: list[dict]
    top_transactions: list[dict]


class TransactionResponse(TransactionCreate):
    id: int
    user : str
    class Config:
        orm_mode = True

# Dependency to get the DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# OAuth2 Bearer token
scheme = OAuth2PasswordBearer(tokenUrl="token")

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Settings
SECRET_KEY = "secret_key_for_jwt"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Helper functions
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_user_by_username(db: Session, username: str):
    return db.query(Users).filter(Users.username == username).first()

def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user or not verify_password(password, user.password):
        return None
    return user

def get_current_user(token: str = Depends(scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user_by_username(db, token_data.username)
    if user is None:
        raise credentials_exception
    return user

# API Routes
@app.post("/token")
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/", response_model=dict)
def create_user_route(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    new_user = Users(username=user.username, password=hash_password(user.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully"}

@app.get("/hello")
def protected_hello(current_user: Users = Depends(get_current_user)):
    return {"message": f"Hello, {current_user.username}"}

@app.post("/transactions/", response_model=TransactionResponse)
def create_transaction_route(
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    db_transaction = Transaction(**transaction.dict())
    db_transaction.user = current_user.username
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

@app.get("/transactions/", response_model=list[TransactionCreate])
def read_transactions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    return db.query(Transaction).filter_by(user=current_user.username).order_by(Transaction.date.asc(), Transaction.id.asc()).offset(skip).limit(limit).all()

@app.get("/transactions/summary/", response_model=SummaryResponse)
def transactions_summary(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    top_count: int = Query(default=5),
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    print(start_date, end_date, top_count)
    # Fetch all transactions within date range
    query = db.query(Transaction).filter(Transaction.user == current_user.username)
    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)

    transaction = query.all()

    # Calculate income vs. expense summary
    total_income = sum(t.amount for t in transaction if t.type == "Credit")
    total_expense = sum(t.amount for t in transaction if t.type == "Debit")
    net_balance = total_income - total_expense

    # Category-wise breakdown
    category_summary = {}
    for t in transaction:
        if t.type == "Debit":
            category_summary[t.category] = category_summary.get(t.category, 0) + t.amount
    category_breakdown = [{"category": k, "amount": v} for k, v in category_summary.items()]

    # Monthly trends
    monthly_summary = {}
    for t in transaction:
        month = t.date.strftime("%B")
        if month not in monthly_summary:
            monthly_summary[month] = {"income": 0, "expense": 0}
        if t.type == "Credit":
            monthly_summary[month]["income"] += t.amount
        else:
            monthly_summary[month]["expense"] += t.amount
    monthly_trends = [{"month": k, "income": v["income"], "expense": v["expense"]} for k, v in monthly_summary.items()]

    # Top transaction
    top_transaction = (
        query.order_by(Transaction.amount.desc())
        .limit(top_count)
        .all()
    )
    top_transaction_list = [
        {
            "name": t.name,
            "amount": t.amount,
            "type": t.type,
            "category": t.category,
            "date": t.date
        } for t in top_transaction
    ]

    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "net_balance": net_balance,
        "category_breakdown": category_breakdown,
        "monthly_trends": monthly_trends,
        "top_transactions": top_transaction_list,
    }
from decouple import config       # Load environment variables from .env file
from rich import print            # For better console output formatting (colors, style)
import logging                    # For logging instead of print — better for production/debug
from datetime import datetime     # Required standard libraries
import random
import faker
from typing import Optional       # noqa: F401 to avoid unused warning for now
# SQLAlchemy core and ORM imports
from sqlalchemy import create_engine, Column, String, Float, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# ----------------------------
# Logging configuration setup
# ----------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ----------------------------
# Faker initialization
# ----------------------------
fake = faker.Faker()

# ----------------------------
# SQLAlchemy base class
# ----------------------------
Base = declarative_base()

# ----------------------------
# Transaction table model
# ----------------------------
class Transaction(Base):
    __tablename__ = 'transactions'

    # Define columns for the table
    transaction_id = Column(String, primary_key=True)
    user_id = Column(String)
    timestamp = Column(DateTime)
    amount = Column(Float)
    currency = Column(String)
    city = Column(String)
    country = Column(String)
    merchant_name = Column(String)
    payment_method = Column(String)
    ip_address = Column(String)
    voucher_code = Column(String)
    affiliate_id = Column(String)

    # Custom string representation for debug/log output
    def __repr__(self):
        return f"<Transaction {self.transaction_id} | {self.amount} {self.currency} | {self.city}, {self.country}>"

# -------------------------------------
# Function to generate fake transaction
# -------------------------------------
def generate_transaction() -> Transaction:
    user = fake.simple_profile()  # generates fake user profile (username, name, etc.)
    return Transaction(
        transaction_id=fake.uuid4(),
        user_id=user['username'],
        timestamp=datetime.utcnow(),  # current UTC timestamp
        amount=round(random.uniform(10, 1000), 2),
        currency=random.choice(['USD', 'GBP', 'MAD']),
        city=fake.city(),
        country=fake.country(),
        merchant_name=fake.company(),
        payment_method=random.choice(['credit_card', 'debit_card', 'online_transfer']),
        ip_address=fake.ipv4(),
        voucher_code=random.choice(['', 'DISCOUNT10', '']),  # sometimes no code
        affiliate_id=fake.uuid4()
    )

# -------------------------------------
# Load PostgreSQL config from .env file
# -------------------------------------
def get_database_url() -> str:
    port = config("POSTGRES_PORT", cast=int)
    user = config("POSTGRES_USER")
    password = config("POSTGRES_PASSWORD")
    db = config("POSTGRES_DB")
    host = config("POSTGRES_HOST", default="localhost")  # default fallback

    # SQLAlchemy expects this URI format
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"

# -------------------------------------
# Initialize DB engine and sessionmaker
# -------------------------------------
def init_db(url: str) -> Session:
    engine = create_engine(url)                 # connects to the database
    Base.metadata.create_all(engine)            # creates table(s) if not exist
    SessionLocal = sessionmaker(bind=engine)    # session factory
    return SessionLocal()

# -------------------------------------
# Main execution block
# -------------------------------------
if __name__ == "__main__":
    db_url = get_database_url()                 # fetch db URL from config
    engine = create_engine(db_url)              # create DB engine
    Base.metadata.create_all(engine)            # ensure tables are created
    SessionLocal = sessionmaker(bind=engine)    # prepare session factory

    # Open a session using context manager (`with` ensures proper cleanup)
    with SessionLocal() as session:
        try:
            transaction = generate_transaction()  # generate mock transaction
            print("[bold green]Generated Transaction:[/bold green]", transaction)

            session.add(transaction)              # add transaction to session
            session.commit()                      # commit transaction to DB
            logger.info("Transaction committed successfully.")
        except Exception as e:
            session.rollback()                    # rollback if any error occurs
            logger.error(f"Transaction failed: {e}")

from sqlalchemy import select, func
from app.models.models import User, Wallet, Merchant, CashbackRule
from app.core.security import hash_password
RULES = [("CANTEEN",200,5000),("STATIONERY",100,2000),("TRANSPORT",300,10000),("HOSTEL",50,20000),("ONLINE",100,3000)]
MERCHANTS = [("Campus Canteen","CANTEEN"),("Campus Stationery","STATIONERY"),
 ("Campus Transport","TRANSPORT"),("Campus Hostel","HOSTEL"),("Campus Online Store","ONLINE")]
def seed_demo_data(db):
    if (db.scalar(select(func.count(User.id))) or 0): return
    u1=User(name="Rahul",email="rahul@finpay.local",password_hash=hash_password("Student@123"),role="STUDENT")
    u2=User(name="Ananya",email="ananya@finpay.local",password_hash=hash_password("Student@123"),role="STUDENT")
    admin=User(name="FinPay Admin",email="admin@finpay.local",password_hash=hash_password("Admin@123"),role="ADMIN")
    db.add_all([u1,u2,admin]); db.flush()
    db.add_all([Wallet(student_id=u1.id,balance_paise=100000,tier="BASIC"),
                Wallet(student_id=u2.id,balance_paise=250000,tier="PRIME")])
    db.add_all([Merchant(name=n,category=c) for n,c in MERCHANTS])
    db.add_all([CashbackRule(category=c,rate_basis_points=r,monthly_cap_paise=cap) for c,r,cap in RULES])
    db.commit()

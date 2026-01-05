from sqlalchemy.orm import Session
from app.models.address_model import Address

class AddressRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_default_address(self, user_id: int):
        return self.db.query(Address).filter(
            Address.user_id == user_id, 
            Address.is_default == True
        ).first()
    
    def creata_default_address(self, user_id: int, data: dict):
        new_address = Address(
            user_id=user_id,
            street_address=data["street_address"],
            ward=data["ward"],
            province_city=data["province_city"],
            recipient_name=data["recipient_name"],
            recipient_phone=data["recipient_phone"],
            is_default=True
        )
        self.db.add(new_address)
        return new_address
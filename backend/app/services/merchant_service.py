from app.repositories.repository import MerchantRepository

class MerchantService:
    @staticmethod
    def list_active_merchants(db):
        return MerchantRepository.active(db)

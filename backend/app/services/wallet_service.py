from app.repositories.repository import WalletRepository

class WalletService:
    @staticmethod
    def get_student_wallet(db, student_id):
        return WalletRepository.by_student(db, student_id)

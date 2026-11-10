from app.core.security import hash_password,verify_password
def test_password_hash():
    value=hash_password("pass123")
    assert value!="pass123"
    assert verify_password("pass123",value)
    assert not verify_password("wrong",value)

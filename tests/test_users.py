
from models import User
from models.users import add_user, find_user, find_user_by_id


def test_user_creation():
    user = User(1, "Иван Петров", "ivan@example.com")
    assert user.id == 1
    assert user.name == "Иван Петров"
    assert user.email == "ivan@example.com"


def test_user_str():
    user = User(1, "Иван Петров", "ivan@example.com")
    assert "Иван Петров" in str(user)
    assert "ivan@example.com" in str(user)


def test_user_from_data():
    data = {"id": 1, "name": "Иван", "email": "i@e.com"}
    user = User.from_data(data)
    assert user.name == "Иван"
    assert user.email == "i@e.com"


def test_user_to_data():
    user = User(1, "Иван", "i@e.com")
    data = user.to_data()
    assert data == {"id": 1, "name": "Иван", "email": "i@e.com"}


def test_add_user():
    users = []
    user = add_user(users, "Иван", "i@e.com")
    assert len(users) == 1
    assert isinstance(user, User)


def test_find_user():
    users = [User(1, "Иван", "ivan@example.com")]
    found = find_user(users, "ivan")
    assert len(found) == 1
    assert found[0].name == "Иван"


def test_find_user_by_id():
    users = [User(1, "Иван", "i@e.com")]
    assert find_user_by_id(users, 1).name == "Иван"
    assert find_user_by_id(users, 99) is None

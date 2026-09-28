from __future__ import annotations


class User:

    def __init__(self, user_id: int, name: str, email: str) -> None:
        self.id = user_id
        self.name = name
        self.email = email

    @classmethod
    def from_data(cls, data: dict) -> "User":
        return cls(
            user_id=data["id"],
            name=data["name"],
            email=data["email"],
        )

    def to_data(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
        }

    def __str__(self) -> str:
        return f"{self.name} <{self.email}>"

    def __repr__(self) -> str:
        return f"User(id={self.id}, name={self.name!r})"


def add_user(users: list[User], name: str, email: str) -> User:
    new_id = max((u.id for u in users), default=0) + 1
    user = User(new_id, name, email)
    users.append(user)
    return user


def find_user(users: list[User], query: str) -> list[User]:
    query_lower = query.lower()
    return [
        u for u in users
        if query_lower in u.name.lower() or query_lower in u.email.lower()
    ]


def find_user_by_id(users: list[User], user_id: int) -> User | None:
    for user in users:
        if user.id == user_id:
            return user
    return None


def show_users(users: list[User]) -> None:
    if not users:
        print("Пользователи отсутствуют.")
        return
    for index, user in enumerate(users, start=1):
        print(f"{index}. {user}")

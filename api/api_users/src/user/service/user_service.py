from api_users.src.user.repository.user_repository import UserRepository
from api_users.src.user.models.models import User


class UserService(object):

    @staticmethod
    def find_all() -> list[User]:
        """ Find all existing Users.

        Returns
        -------
        users : list[User]
            List of founded User objects.
        """
        return UserRepository.find_all()

    @staticmethod
    def find(id: int) -> User | None:
        """ Find user model with a provided id.

        Parameters
        ----------
        id : int
            Id of the user to find.

        Returns
        -------
        user : User
            Founded user object. None otherwise.

        Raises
        ------
        TypeError
            If type of provided id is different than allowed.
        """
        if not isinstance(id, int):
            raise TypeError(f"Illegal type of argument. Id could be only int not {type(id)}")

        return UserRepository.find(id)

    @staticmethod
    def create(user: User) -> int:
        """ Create new instance of User object in database.

        Parameters
        ----------
        user : User
            User object to create.

        Returns
        -------
        id : int
            Id of created user. However when creating failed -1 is returned.

        Raises
        ------
        TypeError
            If type of provided user is different than allowed.
        """
        if not isinstance(user, User):
            raise TypeError(f"Illegal type of argument. User could be only User not {type(user)}")

        result = UserRepository.create(user)
        if result:
            return result
        else:
            return 0

    @staticmethod
    def delete(id: int) -> int:
        """ Delete User object with provided id from database.

        Parameters
        ----------
        id : int
            Id of the user to delete.

        Returns
        -------
        result : int
            1 if operation succeed. 0 otherwise.

        Raises
        ------
        TypeError
            If type of provided id is different than allowed.
        """
        if not isinstance(id, int):
            raise TypeError(f"Illegal type of argument. Id could be only int not {type(id)}")

        result = UserRepository.delete(id)
        if result:
            return result
        else:
            return 0

    @staticmethod
    def update(user: User) -> int:
        """ Update existing user with provided user object
        Parameters
        ----------
        user : User
            User object to add.

        Returns
        -------
        result : int
            ID of updated user. 0 if something failed.

        Raises
        ------
        TypeError
            If type of provided user is different than allowed.
        """
        if not isinstance(user, User):
            raise TypeError(f"Illegal type of argument. User could be only User not {type(user)}")

        result = UserRepository.update(user)
        if result:
            return result
        else:
            return 0

    @staticmethod
    def is_user_port_unique(port: int) -> bool:
        users = UserRepository.find_all()
        users_ports = list(
            map(lambda user: user.port, users)
        )
        return port not in users_ports

from api_users.src.user.models.models import User
from api_users.src import db

from sqlalchemy import exc

from datetime import datetime


class UserRepository(object):

    @staticmethod
    def find_all() -> list[User]:
        """ Find all users.

        Returns
        -------
        users : list[User]
            List of founded users.
        """
        return list(User.query.all())

    @staticmethod
    def find(id: int) -> User | None:
        """ Find user with provided id.

        Parameters
        ----------
        id : int
            ID of user to find.

        Returns
        -------
        user : User | None
            Founded user object if found. Otherwise None.

        Raises
        ------
        TypeError
            If type of provided user is different than allowed.
        """
        if not isinstance(id, int):
            raise ValueError(f"Id could be only type int, not {type(id)}")

        user = User.query.filter_by(id=id).first()
        if user:
            return user
        else:
            return None

    @staticmethod
    def update(user: User) -> int:
        """ Update existing user.

        Parameters
        ----------
        user : User
            User object to update.

        Returns
        -------
        result : int
            Id of updated user if succeed. Otherwise -1.

        Raises
        ------
        TypeError
            If type of provided user is different than allowed.
        """
        if not isinstance(user, User):
            raise TypeError(f"Illegal type of argument. User could be only User object not {type(user)}")

        existing_user = User.query.filter_by(id=user.id).first()
        if existing_user:
            existing_user.date_modified = datetime.now()
            try:
                db.session.add(user)
                db.session.commit()
                return user.id
            except exc.SQLAlchemyError:
                return -1
        else:
            return -1

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
            1 when operation succeed. 0 otherwise.

        Raises
        ------
        TypeError
            If type of provided id is different than allowed.
        """
        if not isinstance(id, int):
            raise TypeError(f"Illegal type of argument. Id could be only int not {type(id)}")

        user = User.query.filter_by(id=id).first()
        if user:
            try:
                db.session.query(User).filter_by(id=id).delete(synchronize_session='fetch')
                db.session.commit()
                return 1
            except exc.SQLAlchemyError:
                return 0
        else:
            return 0

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
            If type of provided user is different than allowed. Default = `FAIL_RETURN_VALUE`
        """
        try:
            db.session.add(user)
            db.session.commit()
            return user.id
        except exc.SQLAlchemyError:
            return -1

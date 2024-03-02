pragma solidity ^0.8.0;

contract LoginRegistry {
    struct User {
        string login;
    }

    mapping(uint256 => User) private users;

    event LoginAdded(uint256 indexed userId, string login, string message);

    function addLogin(uint256 _userId, string memory _login) public {
        require(bytes(_login).length > 0, "Login cannot be empty");
        if (bytes(users[_userId].login).length > 0) {
            emit LoginAdded(_userId, _login, "User ID already exists");
        } else {
            users[_userId] = User(_login);
            emit LoginAdded(_userId, _login, "Successfully added login");
        }
    }

    function getLogin(uint256 _userId) public view returns (string memory) {
        return users[_userId].login;
    }
}

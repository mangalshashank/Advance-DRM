// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract UserDataStorage {
    address private owner;

    modifier onlyOwner() {
        require(msg.sender == owner, "Only the contract owner can call this function");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    mapping(string => bool) private userIdExists;
    mapping(string => bool) private docHashExistsMap;
    mapping(string => string) private docHash;
    mapping(string => string) private docPath;
    mapping(string => string) private username;

    // Function to set user details including userId, username, document hash, and document path
    function setUserDetails(string memory _userId, string memory _userName, string memory _documentHash, string memory _documentPath) public onlyOwner {
        require(bytes(_userId).length > 0, "User ID cannot be empty");
        require(!userIdExists[_userId], "User ID already taken");

        userIdExists[_userId] = true;
        username[_userId] = _userName;

        require(!docHashExistsMap[_documentHash], "Document hash already exists");
        docHash[_userId] = _documentHash;
        docHashExistsMap[_documentHash] = true;

        docPath[_userId] = _documentPath;
    }

    // Function to get a document hash by userId
    function getDocHashByUserId(string memory _userId) public view returns (string memory) {
        return docHash[_userId];
    }

    // Function to get a document path by userId
    function getDocPath(string memory _userId) public view returns (string memory) {
        return docPath[_userId];
    }

    // Function to check if a document hash exists without providing the userId
    function docHashExists(string memory _message) public view returns (bool) {
        return docHashExistsMap[_message];
    }

    // Function to check if a userId exists
    function checkUserIdExists(string memory _userId) public view returns (bool) {
        return userIdExists[_userId];
    }

}

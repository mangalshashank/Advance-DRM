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
    mapping(string => int256) private accessDuration; // New mapping for access duration

    // Function to set user details including userId, username, document hash, document path, and access duration
    function setUserDetails(
        string memory _userId,
        string memory _userName,
        string memory _documentHash,
        string memory _documentPath,
        int256 _duration
    ) public onlyOwner {
        require(bytes(_userId).length > 0, "User ID cannot be empty");
        require(!userIdExists[_userId], "User ID already taken");
        userIdExists[_userId] = true;
        username[_userId] = _userName;
        require(!docHashExistsMap[_documentHash], "Document hash already exists");
        docHashExistsMap[_documentHash] = true;
        docPath[_userId] = _documentPath;
        docHash[_documentHash] = _userId; // Set the document hash to the userId
        accessDuration[_userId] = int256(block.timestamp) + _duration; // Set access duration expiration timestamp
    }

    // Function to get a document path by userId
    function getDocPath(string memory _userId) public view returns (string memory) {
        return docPath[_userId];
    }
    // Function to get a username by userId
    function getUserName(string memory _userId) public view returns (string memory) {
        return username[_userId];
    }

    // Function to check if a document hash exists without providing the userId
    function docHashExists(string memory _message) public view returns (bool) {
        return docHashExistsMap[_message];
    }
    function docHashUserId(string memory _message) public view returns (string memory) {
        return docHash[_message];
    }

    // Function to check if a userId exists
    function checkUserIdExists(string memory _userId) public view returns (bool) {
        return userIdExists[_userId];
    }

    // Function to check if the user is valid to access the document based on the current date
    function isUserValid(string memory _userId) public view returns (int256) {
        int256 dur = accessDuration[_userId] - int256(block.timestamp);
        return dur;
    }

    function extendDuration(string memory _userId, int256 _duration) public onlyOwner {
        accessDuration[_userId] = int256(block.timestamp) + _duration;
    }
}

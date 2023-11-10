const UserDataStorage_Contract = artifacts.require("UserDataStorage");

module.exports = function(deployer) {
  deployer.deploy(UserDataStorage_Contract);
};


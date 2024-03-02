const LoginRegistry = artifacts.require("LoginRegistry");

module.exports = function (deployer) {
  deployer.deploy(LoginRegistry);
};

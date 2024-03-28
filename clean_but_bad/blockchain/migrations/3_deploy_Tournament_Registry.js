const TournamentRegistry = artifacts.require("TournamentRegistry");

module.exports = function (deployer) {
  deployer.deploy(TournamentRegistry);
};
const SimpleContract = artifacts.require("SimpleContract");

contract("SimpleContract", async (accounts) => {
    it("should return the correct value", async () => {
        const simpleContractInstance = await SimpleContract.deployed();
        const result = await simpleContractInstance.getValue();
        assert.equal(result.toNumber(), 42, "The returned value is incorrect");
    });
});

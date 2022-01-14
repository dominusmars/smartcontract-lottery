from brownie import (
    MockV3Aggregator,
    VRFCoordinatorMock,
    LinkToken,
    accounts,
    network,
    config,
    Contract,
)

# from web3 import Web3

LOCAL_BLOCKCHAIN_DEPLOYMENTS = ["development", "ganache-local"]
FOCKED_LOCAL_ENVIRONMENTS = ["mainnet-fork", "mainnet-fork-dev"]


DECIMALS = 8
STARTING_PRICE = 200000000000


def get_account(index=None, id=None):

    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if (
        network.show_active() in LOCAL_BLOCKCHAIN_DEPLOYMENTS
        or network.show_active() in FOCKED_LOCAL_ENVIRONMENTS
    ):
        return accounts[0]

    return accounts.add(config["wallets"]["from_key"])


contract_to_mock = {
    "eth_usd_price": MockV3Aggregator,
    "vrf_coordinator": VRFCoordinatorMock,
    "link_token": LinkToken,
}


def get_contract(contract_name):
    """This function will grab the contract addresses from brownie config if defined, otherwise
    it will deploy mock versions of the necessary contracts and return the mock contracts

        Args:
            contract_name(string)

        Returns:
            brownie.network.contract.ProjectContract: The most recently deployed contract
    """
    contract_type = contract_to_mock[contract_name]
    if network.show_active() in LOCAL_BLOCKCHAIN_DEPLOYMENTS:
        if len(contract_type) <= 0:
            deploy_mock()
        contract = contract_type[-1]
    else:
        contract_address = config["networks"][network.show_active()][contract_name]

        contract = Contract.from_abi(
            contract_type._name, contract_address, contract_type.abi
        )

    return contract


def deploy_mock(decimals=DECIMALS, starting_price=STARTING_PRICE):
    account = get_account()
    MockV3Aggregator.deploy(decimals, starting_price, {"from": account})
    link_token = LinkToken.deploy({"from": account})
    VRFCoordinatorMock.deploy(link_token.address, {"from": account})
    print("Deployed Mock")


def fund_contract_with_link(
    contract_address, account=None, link_token=None, amount=100000000000000000
):
    account = account if account else get_account()
    link_token = link_token if link_token else get_contract("link_token")
    tx = link_token.transfer(contract_address, amount, {"from": account})
    tx.wait(1)
    print(f"Funding sent to {contract_address}")
    return tx


# def deploy_mocks():
#     print(f"The active network is ${network.show_active()}")
#     print("Deploying Mock...")
#     if len(MockV3Aggregator) <= 0:
#         MockV3Aggregator.deploy(DECIMALS, STARTING_PRICE, {"from": get_account()})
#     print("Mocks deployed successfully")
#     return MockV3Aggregator[-1].address

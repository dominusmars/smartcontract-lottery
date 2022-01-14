from brownie import Lottery, accounts, config, network, exceptions
from scripts.deploy_lottery import deploy_lottery
from web3 import Web3
from scripts.helper_functions import (
    LOCAL_BLOCKCHAIN_DEPLOYMENTS,
    get_account,
    fund_contract_with_link,
    get_contract,
)
import pytest


def test_get_entrance_fee():
    if network.show_active() not in LOCAL_BLOCKCHAIN_DEPLOYMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    expected_fee = Web3.toWei(0.025, "ether")
    entrance_fee = lottery.getEnteranceFee()
    assert expected_fee == entrance_fee


def test_cant_enter_without_start():
    if network.show_active() not in LOCAL_BLOCKCHAIN_DEPLOYMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enter(
            {"from": get_account(), "value": lottery.getEnteranceFee() + 1000}
        )


def test_enter_lottery():
    if network.show_active() not in LOCAL_BLOCKCHAIN_DEPLOYMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    # Act
    lottery.enter({"from": account, "value": lottery.getEnteranceFee() + 1000})
    # Assert
    assert lottery.players(0) == account


def test_can_end_lottery():
    if network.show_active() not in LOCAL_BLOCKCHAIN_DEPLOYMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEnteranceFee() + 1000})
    # Act
    fund_contract_with_link(lottery.address)
    lottery.endLottery({"from": account})
    assert lottery.lotteryState() == 2


def test_can_pick_winner():
    if network.show_active() not in LOCAL_BLOCKCHAIN_DEPLOYMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEnteranceFee() + 1000})
    lottery.enter(
        {"from": get_account(index=1), "value": lottery.getEnteranceFee() + 1000}
    )
    lottery.enter(
        {"from": get_account(index=2), "value": lottery.getEnteranceFee() + 1000}
    )
    fund_contract_with_link(lottery.address)
    transaction = lottery.endLottery({"from": account})
    request_id = transaction.events["RequestedRandomness"]["requestId"]
    STATIC_RNG = 777
    get_contract("vrf_coordinator").callBackWithRandomness(
        request_id, STATIC_RNG, lottery.address, {"from": account}
    )

    starting_balance = account.balance()
    balance_of_lottery = lottery.balance()

    assert lottery.recentWinner() == account
    assert lottery.balance() == 0
    assert account.balance() == starting_balance + balance_of_lottery
